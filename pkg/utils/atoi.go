package utils

import (
	"fmt"
	"strconv"
	"time"
)

// Return string to int and ignore error
func Atoi(value string) int {
	num, err := strconv.Atoi(value)
	if err != nil {
		return 0
	}
	return num
}

func ConvertUnixToTime(unixInt string) (time.Time, error) {
	i, err := strconv.ParseInt(unixInt, 10, 64)
	if err != nil {
		return time.Time{}, fmt.Errorf("failed to parse Unix timestamp: %v", err)
	}

	tm := time.Unix(i, 0)
	return tm, nil
}
