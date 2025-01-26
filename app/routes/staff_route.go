package routes

import (
	"github.com/HackIt-Taiwan/HackItDatabaseAPI/app/controllers"
	"github.com/gin-gonic/gin"
)

func StaffRoute(r *gin.RouterGroup) {
	auth := r.Group("/staff")

	auth.POST("/getstaffs", controllers.GetStaffs)
	auth.POST("/create/new", controllers.CreateNewStaff)
	auth.POST("/update/:id", controllers.UpdateStaff)
	auth.POST("/send/verify/:id", controllers.SendCloudflareVerifyEmail)
	auth.POST("/:collection", controllers.SaveData)
	auth.GET("/:collection", controllers.GetData)
}
