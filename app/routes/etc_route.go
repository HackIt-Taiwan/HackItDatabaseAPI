package routes

import (
	"github.com/HackIt-Taiwan/HackItDatabaseAPI/app/controllers"
	"github.com/gin-gonic/gin"
)

func EtcRoute(r *gin.RouterGroup) {
	auth := r.Group("/etc")

	auth.POST("/:collection", controllers.SaveData)
	auth.GET("/:collection", controllers.GetData)
}
