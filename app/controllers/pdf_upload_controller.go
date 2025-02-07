package controllers

import (
	"bytes"
	"fmt"
	"io"
	"path/filepath"

	store "github.com/HackIt-Taiwan/HackItDatabaseAPI/pkg/s3"
	"github.com/HackIt-Taiwan/HackItDatabaseAPI/pkg/utils"
	"github.com/gin-gonic/gin"
)

// UploadPDF handles the PDF upload to S3 and saving the file metadata in the database
func UploadPDF(c *gin.Context) {
	// Parse file from request
	file, err := c.FormFile("pdf")
	if err != nil {
		utils.SimpleResponse(c, 400, "PDF file required", err.Error())
		return
	}

	// Validate file size
	const maxFileSize = 10 * 1024 * 1024 // 10 MB
	if file.Size > maxFileSize {
		utils.SimpleResponse(c, 400, "PDF file too large (> 10MB)", nil)
		return
	}

	// Open the uploaded file
	srcFile, err := file.Open()
	if err != nil {
		utils.SimpleResponse(c, 400, "Error opening PDF file", err)
		return
	}
	defer srcFile.Close()

	// Validate PDF type
	if err := validatePDFType(srcFile); err != nil {
		utils.SimpleResponse(c, 400, "Uploaded file is not a valid PDF", nil)
		return
	}

	// Reset the file pointer to the beginning
	_, err = srcFile.Seek(0, io.SeekStart)
	if err != nil {
		utils.SimpleResponse(c, 500, "Error resetting file pointer", err)
		return
	}

	// Read the entire file content into a buffer
	src := bytes.Buffer{}
	if _, err := src.ReadFrom(srcFile); err != nil {
		utils.SimpleResponse(c, 500, "Error reading PDF file", err)
		return
	}

	// Generate S3 file path and upload the PDF
	filePath := generateFilePath(filepath.Ext(file.Filename))
	if err := uploadToS3(filePath, "application/pdf", src.Bytes()); err != nil {
		utils.SimpleResponse(c, 500, "Error uploading PDF to S3", err)
		return
	}

	// Construct the file URL and send the response
	fileURL := fmt.Sprintf("%s/%s", store.StaticBucketUrl, filePath)
	utils.SimpleResponse(c, 201, "PDF uploaded successfully", fileURL)
}

// validatePDFType checks if the uploaded file is a valid PDF
func validatePDFType(srcFile io.Reader) error {
	magic := make([]byte, 4)
	_, err := srcFile.Read(magic)
	if err != nil && err != io.EOF {
		return fmt.Errorf("error reading file magic number")
	}

	// Check for PDF magic number "%PDF"
	if string(magic) != "%PDF" {
		return fmt.Errorf("invalid PDF file")
	}
	return nil
}