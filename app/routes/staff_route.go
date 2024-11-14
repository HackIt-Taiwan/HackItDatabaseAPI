package routes

import (
	"github.com/HackIt-Taiwan/HackItDatabaseAPI/app/controllers"
	"github.com/gin-gonic/gin"
)

func StaffRoute(r *gin.RouterGroup) {
	auth := r.Group("/staff")

	auth.POST("/create/new", controllers.CreateNewStaff)
	auth.POST("/getstaffs", controllers.GetStaffs)
}