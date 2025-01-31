package controllers

import (
	"bytes"
	"context"
	"crypto/rand"
	"encoding/hex"
	"fmt"
	"io"
	"path/filepath"

	store "github.com/HackIt-Taiwan/HackItDatabaseAPI/pkg/s3"
	"github.com/HackIt-Taiwan/HackItDatabaseAPI/pkg/utils"
	"github.com/aws/aws-sdk-go-v2/service/s3"
	"github.com/gin-gonic/gin"
)

// UploadImage handles the image upload to S3 and saving the image metadata in the database
func UploadImage(c *gin.Context) {
	// Parse image file and course ID from request
	file, err := c.FormFile("image")
	if err != nil {
		utils.SimpleResponse(c, 400, "Image required", err.Error())
		return
	}

	// Validate file size
	const maxFileSize = 10 * 1024 * 1024 // 10 MB
	if file.Size > maxFileSize {
		utils.SimpleResponse(c, 400, "Image too large ( > 10MB)", nil)
		return
	}

	// Open the uploaded file
	srcFile, err := file.Open()
	if err != nil {
		utils.SimpleResponse(c, 400, "Error opening image", err)
		return
	}
	defer srcFile.Close()

	// Validate image type
	contentType, err := validateImageType(srcFile)
	if err != nil {
		utils.SimpleResponse(c, 400, "Uploaded file is not a valid image", nil)
		return
	}

	// Reset the file pointer to the beginning to ensure the full file can be read
	_, err = srcFile.Seek(0, io.SeekStart)
	if err != nil {
		utils.SimpleResponse(c, 500, "Error resetting file pointer", err)
		return
	}

	// Read the entire file content into a buffer
	src := bytes.Buffer{}
	if _, err := src.ReadFrom(srcFile); err != nil {
		utils.SimpleResponse(c, 500, "Error reading image", err)
		return
	}

	// Generate S3 file path and upload the image
	filePath := generateFilePath(filepath.Ext(file.Filename))
	fmt.Println(filePath)
	if err := uploadToS3(filePath, contentType, src.Bytes()); err != nil {
		utils.SimpleResponse(c, 500, "Error uploading file to S3", err)
		return
	}

	// Construct the file URL and send the response
	fileURL := fmt.Sprintf("%s/%s", store.StaticBucketUrl, filePath)
	utils.SimpleResponse(c, 201, "File uploaded successfully", fileURL)
}

// Generate secret file path for the image
func generateFilePath(filename string) (filepath string) {
	secertPath := randomPath(64)
	return secertPath + filename

}

// validateImageType checks if the uploaded file is a valid image
func validateImageType(srcFile io.Reader) (contentType string, err error) {
	magic := make([]byte, 8)
	_, err = srcFile.Read(magic)
	if err != nil && err != io.EOF {
		return "", fmt.Errorf("error reading file magic number")
	}

	isImage, contentType, err := utils.IsValidImageType(magic)
	if err != nil || !isImage {
		return "", fmt.Errorf("invalid image type")
	}
	return contentType, nil
}

// uploadToS3 uploads the image to S3 with the generated file path
func uploadToS3(filePath string, contentType string, fileContent []byte) error {
	_, err := store.Client.PutObject(context.TODO(), &s3.PutObjectInput{
		Bucket:      &store.StaticBucket,
		Key:         &filePath,
		Body:        bytes.NewReader(fileContent),
		ContentType: &contentType, // Assuming contentType is set earlier
	})
	return err
}

func randomPath(n int) string {
	bytes := make([]byte, n)
	_, err := rand.Read(bytes)
	if err != nil {
		panic(err)
	}
	return hex.EncodeToString(bytes)
}
