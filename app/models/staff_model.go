package models

import "time"

type Staff struct {
	UUID             string             `json:"uuid" bson:"_id" binding:"required,uuid"`
	RealName         string             `json:"real_name" bson:"real_name" binding:"required,max=10"`
	Nickname         string             `json:"nickname,omitempty" bson:"nickname,omitempty,max=20"`
	Email            string             `json:"email" bson:"email" binding:"required,email,max=320"`
	PhoneNumber      string             `json:"phone_number" bson:"phone_number" binding:"required,max=10"`
	HighSchoolStage  string             `json:"high_school_stage" bson:"high_school_stage" binding:"required,oneof=高一 高二 高三 高中以上"`
	City             string             `json:"city" bson:"city" binding:"required,max=20"`
	School           string             `json:"school,omitempty" bson:"school,omitempty,max=100"`
	EmergencyContact []EmergencyContact `json:"emergency_contact,omitempty" bson:"emergency_contact,omitempty" binding:"max=2,dive"`
	DiscordID        string             `json:"discord_id,omitempty" bson:"discord_id,omitempty,max=30"`
	Introduction     string             `json:"introduction,omitempty" bson:"introduction,omitempty" binding:"max=1000"`
	CurrentGroup     string             `json:"current_group" bson:"current_group" binding:"required,oneof=HackIt 策劃部 設計部 行政部 公關組 活動企劃組 美術組 資訊組 影音組 行政組 財務組 其他"`
	PermissionLevel  int                `json:"permission_level" bson:"permission_level" binding:"required,oneof=1 2 3 4 5 6"`
	CreatedAt        time.Time          `json:"created_at" bson:"created_at"`
}

type GetStaff struct {
	UUID             string             `json:"uuid" bson:"_id"`
	RealName         string             `json:"real_name" bson:"real_name"`
	Nickname         string             `json:"nickname,omitempty" bson:"nickname,omitempty,max=20"`
	Email            string             `json:"email" bson:"email"`
	PhoneNumber      string             `json:"phone_number" bson:"phone_number"`
	HighSchoolStage  string             `json:"high_school_stage" bson:"high_school_stage"`
	City             string             `json:"city" bson:"city"`
	School           string             `json:"school,omitempty" bson:"school,omitempty,max=100"`
	DiscordID        string             `json:"discord_id,omitempty" bson:"discord_id,omitempty,max=30"`
	Introduction     string             `json:"introduction,omitempty" bson:"introduction,omitempty"`
	CurrentGroup     string             `json:"current_group" bson:"current_group"`
	PermissionLevel  int                `json:"permission_level" bson:"permission_level"`
	CreatedAt        time.Time          `json:"created_at" bson:"created_at"`
}


type EmergencyContact struct {
	Name         string `json:"name" bson:"name" binding:"required,max=10"`
	Relationship string `json:"relationship" bson:"relationship" binding:"required,max=10"`
	Phone        string `json:"phone" bson:"phone" binding:"required,max=10"`
}