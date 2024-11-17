package controllers

import (
	"reflect"
	"strings"
	"time"

	"github.com/HackIt-Taiwan/HackItDatabaseAPI/app/models"
	"github.com/HackIt-Taiwan/HackItDatabaseAPI/app/queries"
	"github.com/HackIt-Taiwan/HackItDatabaseAPI/pkg/encryption"
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

	if err := encryption.EncryptStructFields(&staff); err != nil {
		utils.SimpleResponse(c, 400, "Error encryption your data", err.Error())
		return
	}

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

	staffs, err := queries.GetStaffByAnything(staffRequest)
	if err != nil {
		utils.SimpleResponse(c, 500, "Internal server error or request error", nil)
		return
	}

	utils.SimpleResponse(c, 200, "Successful get staffs", staffs)
}

func UpdateStaff(c *gin.Context) {
	// Validate request body
	UUID := c.Param("id")

	if UUID == "" {
		utils.SimpleResponse(c, 400, "Invalid request", nil)
		return
	}

	var updatedStaffRequest map[string]interface{}

	if err := c.ShouldBindJSON(&updatedStaffRequest); err != nil {
		utils.SimpleResponse(c, 400, "Invalid request", err.Error())
		return
	}

	currentStaff, err := queries.GetStaffQueueById(UUID)
	if err == mongo.ErrNoDocuments {
		utils.SimpleResponse(c, 500, "Staff not found", err.Error())
		return
	} else if err != nil {
		utils.SimpleResponse(c, 500, "Internal server error while checking id", err.Error())
		return
	}

	staffValue := reflect.ValueOf(&currentStaff).Elem() // Ensure the struct is addressable
	staffType := staffValue.Type()

	for key, value := range updatedStaffRequest {
		field := staffValue.FieldByNameFunc(func(fieldName string) bool {
			normalizedFieldName := strings.ReplaceAll(fieldName, "_", "")
			normalizedKey := strings.ReplaceAll(key, "_", "")
			return strings.EqualFold(normalizedFieldName, normalizedKey)
		})

		if field.IsValid() && field.CanSet() {
			fieldInfo, _ := staffType.FieldByNameFunc(func(fieldName string) bool {
				return strings.EqualFold(fieldName, key)
			})

			// Check if the field is marked as encrypted
			isEncrypted := fieldInfo.Tag.Get("encryption") == "true"

			if isEncrypted {
				if _, ok := value.(string); !ok {
					utils.SimpleResponse(c, 400, "Invalid type for encrypted field: "+key, nil)
					return
				}

				// Directly set the value (encryption will happen later)
				field.Set(reflect.ValueOf(value))
			} else {
				newValue := reflect.ValueOf(value)
				if newValue.Type().ConvertibleTo(field.Type()) {
					field.Set(newValue.Convert(field.Type()))
				} else {
					utils.SimpleResponse(c, 400, "Invalid type for field: "+key, nil)
					return
				}
			}
		}
	}

	if err := encryption.EncryptStructFields(&currentStaff); err != nil {
		utils.SimpleResponse(c, 400, "Error encryption your data", err.Error())
		return
	}

	err = queries.UpdateStaffQueue(UUID, currentStaff)
	if err != nil {
		utils.SimpleResponse(c, 500, "Interal server error when updating staff", err.Error())
		return
	}

	utils.SimpleResponse(c, 200, "Successfully updated staff.", currentStaff)
}
