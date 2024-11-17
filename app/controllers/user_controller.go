package controllers

import (
	"reflect"
	"strings"
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

	err = queries.CreateUserQueue(user)
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

func UpdateUser(c *gin.Context) {
	// Validate request body
	UUID := c.Param("id")

	if UUID == "" {
		utils.SimpleResponse(c, 400, "Invalid request", nil)
		return
	}

	var updatedUserReqeust map[string]interface{}

	if err := c.ShouldBindJSON(&updatedUserReqeust); err != nil {
		utils.SimpleResponse(c, 400, "Invalid request", err.Error())
		return
	}

	currentUser, err := queries.GetUserQueueById(UUID)
	if err == mongo.ErrNoDocuments {
		utils.SimpleResponse(c, 500, "User not found.", err.Error())
		return
	} else if err != nil {
		utils.SimpleResponse(c, 500, "Internal server error while checking email", err.Error())
		return
	}

	userValue := reflect.ValueOf(&currentUser).Elem() // Ensure the struct is addressable
	userType := userValue.Type()

	for key, value := range updatedUserReqeust {
		field := userValue.FieldByNameFunc(func(fieldName string) bool {
			normalizedFieldName := strings.ReplaceAll(fieldName, "_", "")
			normalizedKey := strings.ReplaceAll(key, "_", "")
			return strings.EqualFold(normalizedFieldName, normalizedKey)
		})

		if field.IsValid() && field.CanSet() {
			fieldInfo, _ := userType.FieldByNameFunc(func(fieldName string) bool {
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

	err = queries.UpdateUserQueue(currentUser)
	if err != nil {
		utils.SimpleResponse(c, 500, "Interal server error when updating user", err.Error())
		return
	}

	utils.SimpleResponse(c, 200, "Successfully updated user", nil)
}
