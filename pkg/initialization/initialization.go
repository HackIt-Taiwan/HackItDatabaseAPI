package initialization

import (
	"fmt"
	"time"

	"github.com/HackIt-Taiwan/HackItDatabaseAPI/pkg/database"
	"github.com/HackIt-Taiwan/HackItDatabaseAPI/pkg/utils"
	"github.com/charmbracelet/lipgloss"
	"golang.org/x/exp/rand"
)

// Init all need when server start
func Init() {
	database.InitMongoDB()
	utils.InitVariables()
	rand.Seed(uint64(time.Now().UnixNano()))
	utils.InitVaildator()
	fmt.Println(lipgloss.NewStyle().Foreground(lipgloss.Color("#18FD7BFF")).Render("Successfully initialized all necessary services"))
}
