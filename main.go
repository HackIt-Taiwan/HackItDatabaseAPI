package main

import (
	"fmt"
	"log"
	"os"

	"github.com/HackIt-Taiwan/HackItDatabaseAPI/app/routes"
	"github.com/HackIt-Taiwan/HackItDatabaseAPI/pkg/initialization"
	"github.com/HackIt-Taiwan/HackItDatabaseAPI/pkg/middleware"
	"github.com/HackIt-Taiwan/HackItDatabaseAPI/pkg/utils"
	"github.com/gin-gonic/gin"
	"github.com/joho/godotenv"
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

func init() {
	if os.Getenv("GIN_MODE") == "" {
		if err := godotenv.Load(); err != nil {
			log.Fatal("Error loading .env file")
		} else {
			log.Fatal(".env file loaded")
		}
	} else {
		log.Fatal("Environment variable GIN_MODE already set, skipping .env load")
	}
}