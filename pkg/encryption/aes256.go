package encryption

import (
	"crypto/aes"
	"crypto/cipher"
	"crypto/rand"
	"crypto/sha256"
	"crypto/sha512"
	"encoding/base64"
	"encoding/hex"
	"fmt"
	"io"
	"os"
	"reflect"
	"strings"
)

var key []byte

func init() {
	byteKey := sha512.Sum512([]byte(os.Getenv("DATABASE_ENCRYPTION")))
	key = byteKey[:32]
}

func encryptAES256(plaintext string) (string, error) {
	if strings.HasPrefix(plaintext, "AES256:") {
		return "", fmt.Errorf("string already encrypted")
	}

	block, err := aes.NewCipher(key)
	if err != nil {
		return "", err
	}

	ciphertext := make([]byte, aes.BlockSize+len(plaintext))
	iv := ciphertext[:aes.BlockSize]
	if _, err := io.ReadFull(rand.Reader, iv); err != nil {
		return "", err
	}

	stream := cipher.NewCFBEncrypter(block, iv)
	stream.XORKeyStream(ciphertext[aes.BlockSize:], []byte(plaintext))

	encryptedText := base64.StdEncoding.EncodeToString(ciphertext)
	return "AES256:" + encryptedText, nil
}

func decryptAES256(ciphertext string) (string, error) {
	if !strings.HasPrefix(ciphertext, "AES256:") {
		return "", fmt.Errorf("invalid encrypted format")
	}

	ciphertext = ciphertext[len("AES256:"):]

	data, err := base64.StdEncoding.DecodeString(ciphertext)
	if err != nil {
		return "", err
	}

	block, err := aes.NewCipher(key)
	if err != nil {
		return "", err
	}

	iv := data[:aes.BlockSize]
	data = data[aes.BlockSize:]

	stream := cipher.NewCFBDecrypter(block, iv)
	stream.XORKeyStream(data, data)

	return string(data), nil
}

func EncryptFieldsByConfig(data map[string]interface{}) error {
	// 檢查是否有 ignore_encryption 配置
	ignoreConfig, hasIgnore := data["ignore_encryption"].(map[string]interface{})

	// 處理所有字段
	for field, value := range data {
		// 跳過 `ignore_encryption` 配置字段
		if field == "ignore_encryption" {
			continue
		}

		// 如果該字段在 `ignore_encryption` 中，則跳過
		if hasIgnore {
			if _, isIgnored := ignoreConfig[field]; isIgnored {
				continue
			}
		}

		// 跳過以 "_hash" 結尾的字段
		if strings.HasSuffix(field, "_hash") {
			continue
		}

		// 處理字串類型字段
		if strValue, ok := value.(string); ok {
			// 生成哈希值
			hash := sha256.Sum256([]byte(strValue))
			hashHex := hex.EncodeToString(hash[:])

			// 生成加密值
			encryptedValue, err := encryptAES256(strValue)
			if err != nil {
				return err
			}

			// 設置加密字段
			data[field] = encryptedValue

			// 生成哈希字段
			hashFieldName := field + "_hash"
			data[hashFieldName] = hashHex
		}
	}

	// 刪除 `ignore_encryption` 配置
	delete(data, "ignore_encryption")
	return nil
}

func DecryptFieldsByConfig(data map[string]interface{}) error {
	for field, value := range data {
		if strValue, ok := value.(string); ok {
			if strings.HasPrefix(strValue, "AES256:") {
				decryptedValue, err := decryptAES256(strValue)
				if err != nil {
					return err
				}

				data[field] = decryptedValue
			}
		}

		delete(data, field+"_hash")
	}

	return nil
}

// This is use for the get data
func ProcessFieldsForHash(data map[string]interface{}) error {
	ignoreConfig, hasIgnore := data["ignore_encryption"].(map[string]interface{})

	for field, value := range data {
		if field == "ignore_encryption" {
			continue
		}

		if strings.HasSuffix(field, "_hash") {
			continue
		}

		if hasIgnore {
			if _, isIgnored := ignoreConfig[field]; isIgnored {
				continue
			}
		}

		if strValue, ok := value.(string); ok {
			hash := sha256.Sum256([]byte(strValue))
			hashHex := hex.EncodeToString(hash[:])

			hashFieldName := field + "_hash"
			data[hashFieldName] = hashHex

			delete(data, field)
		}
	}

	delete(data, "ignore_encryption")
	return nil
}

func EncryptStructFields(data interface{}) error {
	v := reflect.ValueOf(data).Elem()
	t := v.Type()

	for i := 0; i < t.NumField(); i++ {
		field := t.Field(i)

		if field.Tag.Get("encryption") == "true" {
			fieldValue := v.Field(i)

			if isEmptyValue(fieldValue) {
				continue
			}

			if fieldValue.Kind() == reflect.Slice {
				for j := 0; j < fieldValue.Len(); j++ {
					err := EncryptStructFields(fieldValue.Index(j).Addr().Interface())
					if err != nil {
						return err
					}
				}
			} else if fieldValue.Kind() == reflect.Struct {
				err := EncryptStructFields(fieldValue.Addr().Interface())
				if err != nil {
					return err
				}
			} else if fieldValue.Kind() == reflect.String {
				value := fieldValue.String()
				encryptedValue, err := encryptAES256(value)
				if err != nil {
					if err.Error() == "String already encrypted" {
						continue
					}
					return err
				}
				fieldValue.SetString(encryptedValue)
			}
		}
	}

	return nil
}

func isEmptyValue(v reflect.Value) bool {
	switch v.Kind() {
	case reflect.String:
		return v.Len() == 0
	case reflect.Array, reflect.Slice, reflect.Map, reflect.Chan:
		return v.IsNil() || v.Len() == 0
	case reflect.Ptr, reflect.Interface:
		return v.IsNil()
	default:
		return !v.IsValid() || v.IsZero()
	}
}

func DecryptStructFields(data interface{}) error {
	v := reflect.ValueOf(data).Elem()
	t := v.Type()

	for i := 0; i < t.NumField(); i++ {
		field := t.Field(i)

		if field.Tag.Get("encryption") == "true" {
			fieldValue := v.Field(i)

			if isEmptyValue(fieldValue) {
				continue
			}

			if fieldValue.Kind() == reflect.Slice {
				for j := 0; j < fieldValue.Len(); j++ {
					err := DecryptStructFields(fieldValue.Index(j).Addr().Interface())
					if err != nil {
						return err
					}
				}
			} else if fieldValue.Kind() == reflect.Struct {
				err := DecryptStructFields(fieldValue.Addr().Interface())
				if err != nil {
					return err
				}
			} else if fieldValue.Kind() == reflect.String {
				value := fieldValue.String()
				decryptedValue, err := decryptAES256(value)
				if err != nil {
					return err
				}
				fieldValue.SetString(decryptedValue)
			}
		}
	}

	return nil
}
