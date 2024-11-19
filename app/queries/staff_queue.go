package queries

import (
	"context"
	"errors"
	"fmt"
	"reflect"
	"strings"

	"github.com/HackIt-Taiwan/HackItDatabaseAPI/app/models"
	"github.com/HackIt-Taiwan/HackItDatabaseAPI/pkg/database"
	"github.com/HackIt-Taiwan/HackItDatabaseAPI/pkg/encryption"
	"github.com/HackIt-Taiwan/HackItDatabaseAPI/pkg/utils"
	"go.mongodb.org/mongo-driver/bson"
)

// Get staff by email
func GetStaffQueueByEmail(email string) (models.Staff, error) {
	var staff models.Staff
	err := database.GetCollection("staff").FindOne(context.Background(), bson.M{"email": email}).Decode(&staff)
	return staff, err
}

// Check if discord id already been used
func GetStaffQueueById(ID string) (models.Staff, error) {
	var staff models.Staff
	err := database.GetCollection("staff").FindOne(context.Background(), bson.M{"_id": ID}).Decode(&staff)
	return staff, err
}

// Check if staff discord id already been used
func GetStaffQueueByDiscordID(ID string) (models.Staff, error) {
	var staff models.Staff
	err := database.GetCollection("staff").FindOne(context.Background(), bson.M{"discord_id": ID}).Decode(&staff)
	return staff, err
}

// Get staff by whatever client gives
func GetStaffByAnything(staff models.GetStaff) ([]models.Staff, error) {
	// Prepare an empty slice to hold the results
	var staffList []models.Staff

	// Create query using bson.D to handle dynamic filtering
    flitterQuery := bson.D{}

    val := reflect.ValueOf(staff)
    typ := reflect.TypeOf(staff)

    for i := 0; i < val.NumField(); i++ {
        field := typ.Field(i)
        fieldValue := val.Field(i)
    
        // Retrieve the bson tag from the struct field
        bsonTag := field.Tag.Get("bson")
        if bsonTag == "" || bsonTag == "-" {
            continue // Skip fields without valid bson tags
        }
    
        // Split the bson tag to check for `omitempty`
        tagParts := strings.Split(bsonTag, ",")
        bsonKey := tagParts[0] // The actual key name
    
        // Handle pointer values
        if fieldValue.Kind() == reflect.Ptr {
            if !fieldValue.IsNil() { // Pointer is not nil
                flitterQuery = append(flitterQuery, bson.E{Key: bsonKey, Value: fieldValue.Elem().Interface()})
            }
        } else if fieldValue.IsValid() {
            // Handle non-pointer values
            if !utils.IsZeroValue(fieldValue) { // Non-zero value
                flitterQuery = append(flitterQuery, bson.E{Key: bsonKey, Value: fieldValue.Interface()})
            }
        }
    }
    fmt.Println(flitterQuery)
	// Use Find with the dynamically built query
	cursor, err := database.GetCollection("staff").Find(context.Background(), flitterQuery)
	if err != nil {
		return nil, err
	}
	defer cursor.Close(context.Background())

	// Iterate through the cursor and decode each document into the staff slice
	for cursor.Next(context.Background()) {
		var singleStaff models.Staff
		if err := cursor.Decode(&singleStaff); err != nil {
			return nil, err
		}
		if err := encryption.DecryptStructFields(&singleStaff); err != nil {
			return []models.Staff{}, fmt.Errorf("error decrypt staffs data")
		}
		staffList = append(staffList, singleStaff)
	}

	// Check if any error occurred during the iteration
	if err := cursor.Err(); err != nil {
		return nil, err
	}

	return staffList, nil
}

// Create new staff data
func CreateStaffQueue(staff models.Staff) error {
	_, err := database.GetCollection("staff").InsertOne(context.Background(), staff)
	return err
}

func UpdateStaffQueue(uuid string, staff models.UpdateStaff) error {
    // Define the filter, using the primary key (_id) as the selector
    filter := bson.M{"_id": uuid}

    // Dynamically build the fields to update
    updateFields := bson.D{}
    val := reflect.ValueOf(staff)
    typ := reflect.TypeOf(staff)

    for i := 0; i < val.NumField(); i++ {
        field := typ.Field(i)
        fieldValue := val.Field(i)
    
        // Retrieve the bson tag from the struct field
        bsonTag := field.Tag.Get("bson")
        if bsonTag == "" || bsonTag == "-" {
            continue // Skip fields without valid bson tags
        }
    
        // Split the bson tag to check for `omitempty`
        tagParts := strings.Split(bsonTag, ",")
        bsonKey := tagParts[0] // The actual key name
    
        // Handle pointer values
        if fieldValue.Kind() == reflect.Ptr {
            if !fieldValue.IsNil() { // Pointer is not nil
                updateFields = append(updateFields, bson.E{Key: bsonKey, Value: fieldValue.Elem().Interface()})
            }
        } else if fieldValue.IsValid() {
            // Handle non-pointer values
            if !utils.IsZeroValue(fieldValue) { // Non-zero value
                updateFields = append(updateFields, bson.E{Key: bsonKey, Value: fieldValue.Interface()})
            }
        }
    }

    // Return an error if no fields are available to update
    if len(updateFields) == 0 {
        return errors.New("no fields to update")
    }

    // Wrap the updateFields in $set for partial updates
    update := bson.D{
        {Key: "$set", Value: updateFields},
    }

    // Execute the update operation
    _, err := database.GetCollection("staff").UpdateOne(context.Background(), filter, update)
    if err != nil {
        return err
    }

    return nil
}
