package controllers

import (
	"fmt"

	"github.com/HackIt-Taiwan/HackItDatabaseAPI/app/queries"
	"github.com/HackIt-Taiwan/HackItDatabaseAPI/pkg/encryption"
	"github.com/HackIt-Taiwan/HackItDatabaseAPI/pkg/utils"
	"github.com/gin-gonic/gin"
	"go.mongodb.org/mongo-driver/bson"
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
		utils.SimpleResponse(c, 500, "Error encrypt field", err.Error())
		return
	}

	err = queries.CreateData(collection, requestData)
	if err != nil {
		utils.SimpleResponse(c, 500, "Internal server error", err.Error())
		return
	}
	utils.SimpleResponse(c, 201, "Successfully created new data", nil)
}

func GetAllData(c *gin.Context) {
	collection := c.Param("collection")

	filter := map[string]interface{}{
		"status": map[string]interface{}{
			"$in": []string{"已拒絕", "已接受", "資料確認中"},
		},
	}

	err := encryption.ProcessFieldsForHash(filter)
	if err != nil {
		fmt.Println("Error encrypting fields:", err)
		utils.SimpleResponse(c, 500, "Encryption error", err.Error())
		return
	}

	results, err := queries.GetData(collection, filter)
	if err != nil {
		utils.SimpleResponse(c, 500, "Internal server error", err.Error())
		return
	}

	utils.SimpleResponse(c, 200, "Successfully acquired data", results)
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

	utils.SimpleResponse(c, 200, "Successfully acquired data", results)
}

func EditData(c *gin.Context) {
	var requestData map[string]interface{}
	collection := c.Param("collection")

	if err := c.ShouldBindJSON(&requestData); err != nil {
		utils.SimpleResponse(c, 400, "Invalid request", err.Error())
		return
	}

	id, exists := requestData["_id"]
	if !exists {
		utils.SimpleResponse(c, 400, "Missing _id field", "The _id field is required for updates.")
		return
	}

	err := encryption.EncryptFieldsByConfig(requestData)
	if err != nil {
		fmt.Println("Error encrypting fields:", err)
		utils.SimpleResponse(c, 500, "Encryption error", err.Error())
		return
	}

	err = queries.UpdateDataByID(collection, id, requestData)
	if err != nil {
		utils.SimpleResponse(c, 500, "Internal server error", err.Error())
		return
	}

	utils.SimpleResponse(c, 200, "Data successfully updated", nil)
}
