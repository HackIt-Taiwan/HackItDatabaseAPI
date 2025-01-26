package controllers

import (
	"fmt"

	"github.com/HackIt-Taiwan/HackItDatabaseAPI/app/queries"
	"github.com/HackIt-Taiwan/HackItDatabaseAPI/pkg/encryption"
	"github.com/HackIt-Taiwan/HackItDatabaseAPI/pkg/utils"
	"github.com/gin-gonic/gin"
)

func SaveData(c *gin.Context) {
	var requestData map[string]interface{}
	collection := c.Param("collection")
	if err := c.ShouldBindJSON(&requestData); err != nil {
		utils.SimpleResponse(c, 400, "Invalid request", err.Error())
		return
	}

	err := encryption.EncryptFieldsByConfig(requestData)
	if err != nil {
		fmt.Println("Error encrypting fields:", err)
		return
	}

	err = queries.CreateData(collection, requestData)
	if err != nil {
		utils.SimpleResponse(c, 500, "Internal server error", err.Error())
		return
	}
	utils.SimpleResponse(c, 201, "Successful create new data", nil)
}

func GetData(c *gin.Context) {
	var requestData map[string]interface{}
	collection := c.Param("collection")

	if err := c.ShouldBindJSON(&requestData); err != nil {
		utils.SimpleResponse(c, 400, "Invalid request", err.Error())
		return
	}

	err := encryption.ProcessFieldsForHash(requestData)
	if err != nil {
		fmt.Println("Error encrypting fields:", err)
		utils.SimpleResponse(c, 500, "Encryption error", err.Error())
		return
	}

	results, err := queries.GetData(collection, requestData)
	if err != nil {
		utils.SimpleResponse(c, 500, "Internal server error", err.Error())
		return
	}

	utils.SimpleResponse(c, 201, "Successful create new data", results)
}