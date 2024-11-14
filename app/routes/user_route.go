package routes

import (
	"github.com/HackIt-Taiwan/HackItDatabaseAPI/app/controllers"
	"github.com/gin-gonic/gin"
)

func UserRoute(r *gin.RouterGroup) {
	auth := r.Group("/user")

	auth.POST("/create/new", controllers.CreateNewUser)
	auth.POST("/getusers", controllers.GetUsers)
}