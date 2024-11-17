package queries

import (
	"context"
	"errors"

	"github.com/HackIt-Taiwan/HackItDatabaseAPI/app/models"
	"github.com/HackIt-Taiwan/HackItDatabaseAPI/pkg/database"
	"go.mongodb.org/mongo-driver/bson"
)

// Get user by email
func GetUserQueueByEmail(email string) (models.User, error) {
	var user models.User
	err := database.GetCollection("user").FindOne(context.Background(), bson.M{"email": email}).Decode(&user)
	return user, err
}

// Check if discord id already been used
func GetUserQueueById(ID string) (models.User, error) {
	var user models.User
	err := database.GetCollection("user").FindOne(context.Background(), bson.M{"_id": ID}).Decode(&user)
	return user, err
}

// Get user by whatever client gives
func GetuserByAnything(user models.GetUser) ([]models.User, error) {
	// Prepare an empty slice to hold the results
	var userList []models.User

	// Create query using bson.D to handle dynamic filtering
	query := bson.D{}

	// Add conditions to the query dynamically based on provided fields
	if user.UUID != "" {
		query = append(query, bson.E{Key: "_id", Value: user.UUID})
	}
	if user.Name != "" {
		query = append(query, bson.E{Key: "real_name", Value: user.Name})
	}

	// Use Find with the dynamically built query
	cursor, err := database.GetCollection("user").Find(context.Background(), query)
	if err != nil {
		return nil, err
	}
	defer cursor.Close(context.Background())

	// Iterate through the cursor and decode each document into the user slice
	for cursor.Next(context.Background()) {
		var singleuser models.User
		if err := cursor.Decode(&singleuser); err != nil {
			return nil, err
		}
		userList = append(userList, singleuser)
	}

	// Check if any error occurred during the iteration
	if err := cursor.Err(); err != nil {
		return nil, err
	}

	return userList, nil
}

// Create new user data
func CreateUserQueue(user models.User) error {
	_, err := database.GetCollection("user").InsertOne(context.Background(), user)
	return err
}

func UpdateUserQueue(user models.User) error {
    // Define the filter
    filter := bson.M{"_id": user.UUID}

    // Wrap the struct in $set to update only the fields provided
    update := bson.M{"$set": user}

    // Perform the update
    result, err := database.GetCollection("staff").UpdateOne(context.Background(), filter, update)
    if err != nil {
        return err
    }

    if result.MatchedCount == 0 {
        return errors.New("no matching document found to update")
    }

    return nil
}
