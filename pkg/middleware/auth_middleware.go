package middleware

import (
	"os"

	"github.com/gin-gonic/gin"
)

func TokenAuthMiddleware() gin.HandlerFunc {
    return func(c *gin.Context) {
        expectedToken := os.Getenv("AUTH_TOKEN")
        if expectedToken == "" {
            c.AbortWithStatusJSON(500, gin.H{"error": "Server configuration error"})
            return
        }

        token := c.GetHeader("Authorization")
        if token != "Bearer "+expectedToken {
            c.AbortWithStatusJSON(403, gin.H{"error": "Invalid or missing token"})
            return
        }

        c.Next()
    }
}
