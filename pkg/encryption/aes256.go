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
		return "", fmt.Errorf("String already encrypted")
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
			if v.Field(i).Kind() == reflect.Slice {
				slice := v.Field(i)
				for j := 0; j < slice.Len(); j++ {
					err := EncryptStructFields(slice.Index(j).Addr().Interface())
					if err != nil {
						return err
					}
				}
			} else {
				value := v.Field(i).String()
				encryptedValue, err := encryptAES256(value)
				if err != nil {
					if err.Error() == "String already encrypted" { // Fallback for updating.
						continue
					}
					return err
				}
				v.Field(i).SetString(encryptedValue)
			}
		}
	}
	return nil
}

func DecryptStructFields(data interface{}) error {
	v := reflect.ValueOf(data).Elem()
	t := v.Type()

	for i := 0; i < t.NumField(); i++ {
		field := t.Field(i)
		if field.Tag.Get("encryption") == "true" {
			if v.Field(i).Kind() == reflect.Slice {
				slice := v.Field(i)
				for j := 0; j < slice.Len(); j++ {
					err := DecryptStructFields(slice.Index(j).Addr().Interface())
					if err != nil {
						return err
					}
				}
			} else {
				value := v.Field(i).String()
				decryptedValue, err := decryptAES256(value)
				if err != nil {
					return err
				}
				v.Field(i).SetString(decryptedValue)
			}
		}
	}
	return nil
}

