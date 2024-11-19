package utils

import (
	"log"
	"reflect"
	"time"

	"github.com/gin-gonic/gin/binding"
	"github.com/go-playground/validator/v10"
)

var LangList = []string{"en", "es", "zh-tw", "zh-cn"}

type LangLocal string

const (
	English  LangLocal = "en"
	Spanish  LangLocal = "es"
	ChineseTW LangLocal = "zh-tw"
	ChineseCN LangLocal = "zh-cn"
)

var langLocalValidator validator.Func = func(fl validator.FieldLevel) bool {
    lang := fl.Field().String()
    for _, validLang := range LangList {
        if lang == validLang {
            return true
        }
    }
    return false
}

var unixTimestampValidator validator.Func = func(fl validator.FieldLevel) bool {
	timestamp := fl.Field().Int()
	return timestamp >= 0 && timestamp <= time.Now().Unix()
}

func InitVaildator() {
	if v, ok := binding.Validator.Engine().(*validator.Validate); ok {
		v.RegisterValidation("lang", langLocalValidator)
		v.RegisterValidation("unixtimestamp", unixTimestampValidator)
	} else {
		log.Fatalf("error register vaildatioon")
	}
}

func IsZeroValue(value reflect.Value) bool {
    switch value.Kind() {
    case reflect.String:
        return value.Len() == 0
    case reflect.Int, reflect.Int8, reflect.Int16, reflect.Int32, reflect.Int64:
        return value.Int() == 0
    case reflect.Uint, reflect.Uint8, reflect.Uint16, reflect.Uint32, reflect.Uint64:
        return value.Uint() == 0
    case reflect.Float32, reflect.Float64:
        return value.Float() == 0
    case reflect.Bool:
        return !value.Bool()
    default:
        return false
    }
}