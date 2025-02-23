package queries

import (
	"context"

	"github.com/HackIt-Taiwan/HackItDatabaseAPI/pkg/database"
	"github.com/HackIt-Taiwan/HackItDatabaseAPI/pkg/encryption"
	"go.mongodb.org/mongo-driver/bson"
	"go.mongodb.org/mongo-driver/mongo"
	"go.mongodb.org/mongo-driver/mongo/options"
)

func CreateData(collection string, data map[string]interface{}) error {
	_, err := database.GetCollection(collection).InsertOne(context.Background(), data)
	return err
}

func GetData(collection string, filter map[string]interface{}) ([]map[string]interface{}, error) {
	var results []map[string]interface{}
	cursor, err := database.GetCollection(collection).Find(context.Background(), filter)
	if err != nil {
		return nil, err
	}
	defer cursor.Close(context.Background())

	for cursor.Next(context.Background()) {
		var result map[string]interface{}
		if err := cursor.Decode(&result); err != nil {
			return nil, err
		}

		if err := encryption.DecryptFieldsByConfig(result); err != nil {
			continue
		}

		results = append(results, result)
	}

	if err := cursor.Err(); err != nil {
		return nil, err
	}

	return results, nil
}

func GetDataByDateAndFilter(collection string, filter map[string]interface{}) ([]map[string]interface{}, error) {
	// Create options for sorting by date (assuming date field is named "date")
	opts := options.Find().SetSort(bson.D{{Key: "completeAt", Value: -1}}) // -1 for descending, 1 for ascending

	var results []map[string]interface{}
	cursor, err := database.GetCollection(collection).Find(context.Background(), filter, opts)
	if err != nil {
		return nil, err
	}
	defer cursor.Close(context.Background())

	for cursor.Next(context.Background()) {
		var result map[string]interface{}
		if err := cursor.Decode(&result); err != nil {
			return nil, err
		}
		if err := encryption.DecryptFieldsByConfig(result); err != nil {
			continue
		}
		results = append(results, result)
	}

	if err := cursor.Err(); err != nil {
		return nil, err
	}
	return results, nil
}

func UpdateDataByID(collection string, id interface{}, newData map[string]interface{}) error {
	delete(newData, "_id")

	filter := bson.M{"_id": id}
	update := bson.M{"$set": newData}

	result, err := database.GetCollection(collection).UpdateOne(context.Background(), filter, update)
	if err != nil {
		return err
	}

	if result.MatchedCount == 0 {
		return mongo.ErrNoDocuments
	}

	return nil
}

