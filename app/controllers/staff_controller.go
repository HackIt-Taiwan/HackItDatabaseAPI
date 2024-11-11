package controllers

import (
	"time"

	"github.com/HackIt-Taiwan/HackItDatabaseAPI/app/models"
	"github.com/HackIt-Taiwan/HackItDatabaseAPI/app/queries"
	"github.com/HackIt-Taiwan/HackItDatabaseAPI/pkg/utils"
	"github.com/gin-gonic/gin"
	"go.mongodb.org/mongo-driver/mongo"
)

func CreateNewStaff(c *gin.Context) {
	var staff models.Staff
	// Validate request body
	if err := c.ShouldBindJSON(&staff); err != nil {
		utils.SimpleResponse(c, 400, "Invalid request", err.Error())
		return
	}
	staff.CreatedAt = time.Now()
	// Check if email already been used
	_, err := queries.GetStaffQueueByEmail(staff.Email)
	if err == nil {
		utils.SimpleResponse(c, 400, "Email already been used", nil)
		return
	} else if err != mongo.ErrNoDocuments {
		utils.SimpleResponse(c, 500, "Internal server error while checking email", err.Error())
		return
	}

	// Check if staff id  already been used
	_, err = queries.GetStaffQueueById(staff.UUID)
	if err == nil {
		utils.SimpleResponse(c, 400, "ID already been used", nil)
		return
	} else if err != mongo.ErrNoDocuments {
		utils.SimpleResponse(c, 500, "Internal server error while checking email", err.Error())
		return
	}

	// Check if staff discord id already been used
	_, err = queries.GetStaffQueueByDiscordID(staff.DiscordID)
	if err == nil {
		utils.SimpleResponse(c, 400, "Discord ID already been used", nil)
		return
	} else if err != mongo.ErrNoDocuments {
		utils.SimpleResponse(c, 500, "Internal server error while checking email", err.Error())
		return
	}

	err = queries.CreateStaffQueue(staff)
	if err != nil {
		utils.SimpleResponse(c, 500, "Internal server error", err.Error())
		return
	}

	utils.SimpleResponse(c, 201, "Successful create new staff", nil)
}

func GetStaffs(c *gin.Context) {
	var staffRequest models.GetStaff
	// Validate request body
	if err := c.ShouldBindJSON(&staffRequest); err != nil {
		utils.SimpleResponse(c, 400, "Invalid request", err.Error())
		return
	}

	staff, err := queries.GetStaffByAnything(staffRequest)
	if err == nil {
		utils.SimpleResponse(c, 400, "Email already been used", nil)
		return
	}

	utils.SimpleResponse(c, 200, "Successful get staffs", staff)
}