package models

import "time"

type Staff struct {
	UUID             string             `json:"uuid" bson:"_id" binding:"required,uuid"`
	RealName         string             `json:"real_name" bson:"real_name" binding:"required,max=10" encryption:"true"`
	Nickname         string             `json:"nickname,omitempty" bson:"nickname,omitempty" binding:"max=20" encryption:"true"`
	Email            string             `json:"email" bson:"email" binding:"required,email,max=320"`
	OfficialEmail    string             `json:"official_email" bson:"official_email" binding:"required,email,max=320"`
	PhoneNumber      string             `json:"phone_number" bson:"phone_number" binding:"required,max=10" encryption:"true"`
	HighSchoolStage  string             `json:"high_school_stage" bson:"high_school_stage" binding:"required,oneof=高一 高二 高三 高中以上"`
	City             string             `json:"city" bson:"city" binding:"required,max=20" encryption:"true"`
	School           string             `json:"school,omitempty" bson:"school,omitempty" binding:"max=100" encryption:"true"`
	NationalID       string             `json:"national_id" bson:"national_id,omitempty" binding:"required,len=10"`
	StudentCard      Card               `json:"student_card,omitempty" bson:"student_card,omitempty" encryption:"true"`
	IDCard           Card               `json:"id_card,omitempty" bson:"id_card,omitempty" encryption:"true"`
	EmergencyContact []EmergencyContact `json:"emergency_contact,omitempty" bson:"emergency_contact,omitempty" binding:"min=1,max=2,dive" encryption:"true"`
	DiscordID        string             `json:"discord_id,omitempty" bson:"discord_id,omitempty" binding:"max=30"`
	Introduction     string             `json:"introduction,omitempty" bson:"introduction,omitempty" binding:"max=1000" encryption:"true"`
	CurrentGroup     string             `json:"current_group" bson:"current_group" binding:"required,oneof=HackIt 行政部 公共事務部 策劃部 媒體影像部 資訊科技部"`
	PermissionLevel  int                `json:"permission_level" bson:"permission_level" binding:"required,oneof=1 2 3 4 5 6 0"`
	CreatedAt        time.Time          `json:"created_at" bson:"created_at"`
}

type Card struct {
	Front string `json:"front,omitempty" bson:"front,omitempty" encryption:"true"`
	Back  string `json:"back,omitempty" bson:"back,omitempty" encryption:"true"`
}

type UpdateStaff struct {
	RealName         string             `json:"real_name,omitempty" bson:"real_name,omitempty" binding:"max=10" encryption:"true"`
	Nickname         string             `json:"nickname,omitempty" bson:"nickname,omitempty" binding:"max=20" encryption:"true"`
	Email            string             `json:"email,omitempty" bson:"email,omitempty" binding:"email,max=320"`
	OfficialEmail    string             `json:"offical_email,omitempty" bson:"official_email,omitempty" binding:"email,max=320"`
	PhoneNumber      string             `json:"phone_number,omitempty" bson:"phone_number,omitempty" binding:"max=20" encryption:"true"`
	HighSchoolStage  string             `json:"high_school_stage,omitempty" bson:"high_school_stage,omitempty" binding:"oneof=高一 高二 高三 高中以上"`
	City             string             `json:"city,omitempty" bson:"city,omitempty" binding:"max=20" encryption:"true"`
	School           string             `json:"school,omitempty" bson:"school,omitempty" binding:"max=100" encryption:"true"`
	NationalID       string             `json:"national_id,omitempty" bson:"national_id,omitempty" binding:"len=10"`
	StudentCard      Card               `json:"student_card,omitempty" bson:"student_card,omitempty" encryption:"true"`
	IDCard           Card               `json:"id_card,omitempty" bson:"id_card,omitempty" encryption:"true"`
	EmergencyContact []EmergencyContact `json:"emergency_contact,omitempty" bson:"emergency_contact,omitempty" binding:"max=2,dive" encryption:"true"`
	DiscordID        string             `json:"discord_id,omitempty" bson:"discord_id,omitempty" binding:"max=30"`
	Introduction     string             `json:"introduction,omitempty" bson:"introduction,omitempty" binding:"max=1000" encryption:"true"`
	CurrentGroup     string             `json:"current_group,omitempty" bson:"current_group,omitempty" binding:"oneof=HackIt 策劃部 設計部 行政部 公關組 活動企劃組 美術組 資訊組 影音組 行政組 財務組 其他"`
	PermissionLevel  int                `json:"permission_level,omitempty" bson:"permission_level,omitempty" binding:"oneof=1 2 3 4 5 6"`
}

type GetStaff struct {
	UUID            string `json:"uuid" bson:"_id"`
	Email           string `json:"email" bson:"email"`
	OfficialEmail   string `json:"official_email" bson:"official_email"`
	HighSchoolStage string `json:"high_school_stage" bson:"high_school_stage"`
	DiscordID       string `json:"discord_id,omitempty" bson:"discord_id,omitempty"`
	CurrentGroup    string `json:"current_group" bson:"current_group"`
	PermissionLevel int    `json:"permission_level" bson:"permission_level"`
}

type EmergencyContact struct {
	Name         string `json:"name" bson:"name" binding:"required,max=10" encryption:"true"`
	Relationship string `json:"relationship" bson:"relationship" binding:"required,max=10" encryption:"true"`
	Phone        string `json:"phone" bson:"phone" binding:"required,max=10" encryption:"true"`
}
