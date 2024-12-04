package encryption

import (
	"crypto/aes"
	"crypto/cipher"
	"crypto/rand"
	"crypto/sha512"
	"encoding/base64"
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
