package queries

import (
	"context"

	"github.com/HackIt-Taiwan/HackItDatabaseAPI/app/models"
	"github.com/HackIt-Taiwan/HackItDatabaseAPI/pkg/database"
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

	// Use Find instead of FindOne to get multiple documents
	cursor, err := database.GetCollection("staff").Find(context.Background(), staff)
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