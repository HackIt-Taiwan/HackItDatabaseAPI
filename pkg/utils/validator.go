package utils

import (
	"log"
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
