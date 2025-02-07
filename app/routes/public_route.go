package routes

import (
	"github.com/HackIt-Taiwan/HackItDatabaseAPI/app/controllers"
	"github.com/gin-gonic/gin"
)

func PublicRoute(r *gin.RouterGroup) {
	auth := r.Group("/public")

	auth.POST("/image/upload", controllers.UploadImage)
	auth.POST("/pdf/upload", controllers.UploadPDF)
}
