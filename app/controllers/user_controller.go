package controllers

import (
	"time"

	"github.com/HackIt-Taiwan/HackItDatabaseAPI/app/models"
	"github.com/HackIt-Taiwan/HackItDatabaseAPI/app/queries"
	"github.com/HackIt-Taiwan/HackItDatabaseAPI/pkg/utils"
	"github.com/gin-gonic/gin"
	"go.mongodb.org/mongo-driver/mongo"
)

func CreateNewUser(c *gin.Context) {
	var user models.User
	// Validate request body
	if err := c.ShouldBindJSON(&user); err != nil {
		utils.SimpleResponse(c, 400, "Invalid request", err.Error())
		return
	}
	user.CreatedAt = time.Now()
	// Check if email already been used
	_, err := queries.GetUserQueueByEmail(user.Email)
	if err == nil {
		utils.SimpleResponse(c, 400, "Email already been used", nil)
		return
	} else if err != mongo.ErrNoDocuments {
		utils.SimpleResponse(c, 500, "Internal server error while checking email", err.Error())
		return
	}

	// Check if user id  already been used
	_, err = queries.GetUserQueueById(user.UUID)
	if err == nil {
		utils.SimpleResponse(c, 400, "ID already been used", nil)
		return
	} else if err != mongo.ErrNoDocuments {
		utils.SimpleResponse(c, 500, "Internal server error while checking email", err.Error())
		return
	}

	err = queries.CreateuserQueue(user)
	if err != nil {
		utils.SimpleResponse(c, 500, "Internal server error", err.Error())
		return
	}

	utils.SimpleResponse(c, 201, "Successful create new user", nil)
}


func GetUsers(c *gin.Context) {
	var userRequest models.GetUser
	// Validate request body
	if err := c.ShouldBindJSON(&userRequest); err != nil {
		utils.SimpleResponse(c, 400, "Invalid request", err.Error())
		return
	}

	staffs, err := queries.GetuserByAnything(userRequest)
	if err != nil {
		utils.SimpleResponse(c, 500, "Internal server error or request error", nil)
		return
	}

	utils.SimpleResponse(c, 200, "Successful get users", staffs)
}