package cf

import (
	"log"
	"os"

	"github.com/cloudflare/cloudflare-go"
)

var Api *cloudflare.API

func init() {
	var err error
	Api, err = 	cloudflare.NewWithAPIToken(os.Getenv("CLOUDFLARE_API_TOKEN"))

	if err != nil {
		log.Fatal(err)
	}
}