package routes

import (
	"github.com/HackIt-Taiwan/HackItDatabaseAPI/app/controllers"
	"github.com/gin-gonic/gin"
)

func EtcRoute(r *gin.RouterGroup) {
	auth := r.Group("/etc")

	auth.POST("/create/:collection", controllers.SaveData)
	auth.POST("/get/:collection", controllers.GetData)
	auth.POST("/edit/:collection", controllers.EditData)
	auth.POST("/image/upload", controllers.EditData)
}
