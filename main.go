package main

import (
	"fmt"
	"os"

	"github.com/HackIt-Taiwan/HackItDatabaseAPI/app/routes"
	"github.com/HackIt-Taiwan/HackItDatabaseAPI/pkg/initialization"
	"github.com/HackIt-Taiwan/HackItDatabaseAPI/pkg/middleware"
	"github.com/HackIt-Taiwan/HackItDatabaseAPI/pkg/utils"
	"github.com/gin-gonic/gin"
	_ "github.com/joho/godotenv/autoload"
	_ "github.com/HackIt-Taiwan/HackItDatabaseAPI/pkg/cloudflare"
)

func main() {
	root := gin.New()

	root.SetTrustedProxies([]string{"127.0.0.1"})
	root.Use(middleware.CustomLogger())
	// Init all dependencies
	initialization.Init()

	r := root.Group("/api/v" + os.Getenv("VERSION"))
	r.Use(middleware.TokenAuthMiddleware())

	utils.PrintAppBanner()

	routes.StaffRoute(r)
	routes.UserRoute(r)

	if err := root.Run(); err != nil {
		fmt.Printf("Server failed to start: %v\n", err)
	}
}
