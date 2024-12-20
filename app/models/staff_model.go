package models

import "time"

type Staff struct {
	UUID               string             `json:"uuid" bson:"_id" binding:"required,uuid"`
	RealName           string             `json:"real_name" bson:"real_name" binding:"required,max=10" encryption:"true"`
	Nickname           string             `json:"nickname,omitempty" bson:"nickname,omitempty" binding:"max=20" encryption:"true"`
	Email              string             `json:"email" bson:"email" binding:"required,email,max=320"`
	OfficialEmail      string             `json:"official_email" bson:"official_email" binding:"required,email,max=320"`
	PhoneNumber        string             `json:"phone_number" bson:"phone_number" binding:"required,max=10" encryption:"true"`
	HighSchoolStage    string             `json:"high_school_stage" bson:"high_school_stage" binding:"required,oneof=高一 高二 高三 高中以上"`
	City               string             `json:"city" bson:"city" binding:"required,max=20" encryption:"true"`
	School             string             `json:"school,omitempty" bson:"school,omitempty" binding:"max=100" encryption:"true"`
	NationalID         string             `json:"national_id" bson:"national_id,omitempty" binding:"max=10"`
	StudentCard        Card               `json:"student_card,omitempty" bson:"student_card,omitempty" encryption:"true"`
	IDCard             Card               `json:"id_card,omitempty" bson:"id_card,omitempty" encryption:"true"`
	EmergencyContact   []EmergencyContact `json:"emergency_contact,omitempty" bson:"emergency_contact,omitempty" binding:"min=1,max=2,dive" encryption:"true"`
	DiscordID          string             `json:"discord_id,omitempty" bson:"discord_id,omitempty" binding:"max=30"`
	Introduction       string             `json:"introduction,omitempty" bson:"introduction,omitempty" binding:"max=1000" encryption:"true"`
	Choicereason       string             `json:"choicereason,omitempty" bson:"choicereason,omitempty" binding:"max=1000" encryption:"true"`
	RelevantExperience string             `json:"relevant_experience,omitempty" bson:"relevant_experience,omitempty" binding:"max=1000" encryption:"true"`
	SignatureUrl       string             `json:"signature_url,omitempty" bson:"signature_url,omitempty" binding:"max=200"`
	CurrentGroup       string             `json:"current_group" bson:"current_group" binding:"required,oneof=HackIt 行政部 策劃部 資訊科技部 公共事務部 媒體影像部 行政部 企劃組 進度管理組 視覺影像組 平面設計組 公關組 社群管理組 pending"`
	PermissionLevel    int                `json:"permission_level" bson:"permission_level" binding:"required,oneof=1 2 3 4 5 6 0 10"`
	TeamLeader         string             `json:"team_leader,omitempty" bson:"team_leader,omitempty" binding:"max=30"`
	ApplyMessage       string             `json:"apply_message,omitempty" bson:"apply_message,omitempty" binding:"max=200"`
	CreatedAt          time.Time          `json:"created_at" bson:"created_at"`
}

type Card struct {
	Front string `json:"front,omitempty" bson:"front,omitempty" encryption:"true"`
	Back  string `json:"back,omitempty" bson:"back,omitempty" encryption:"true"`
}

type UpdateStaff struct {
	RealName         string             `json:"real_name,omitempty" bson:"real_name,omitempty" binding:"max=10" encryption:"true"`
	Nickname         string             `json:"nickname,omitempty" bson:"nickname,omitempty" binding:"max=20" encryption:"true"`
	Email            string             `json:"email,omitempty" bson:"email,omitempty" binding:"max=320"`
	OfficialEmail    string             `json:"official_email,omitempty" bson:"official_email,omitempty" binding:"max=320"`
	PhoneNumber      string             `json:"phone_number,omitempty" bson:"phone_number,omitempty" binding:"max=20" encryption:"true"`
	HighSchoolStage  string             `json:"high_school_stage,omitempty" bson:"high_school_stage,omitempty"`
	City             string             `json:"city,omitempty" bson:"city,omitempty" binding:"max=20" encryption:"true"`
	School           string             `json:"school,omitempty" bson:"school,omitempty" binding:"max=100" encryption:"true"`
	NationalID       string             `json:"national_id,omitempty" bson:"national_id,omitempty" binding:"max=10"`
	StudentCard      Card               `json:"student_card,omitempty" bson:"student_card,omitempty" encryption:"true"`
	IDCard           Card               `json:"id_card,omitempty" bson:"id_card,omitempty" encryption:"true"`
	EmergencyContact []EmergencyContact `json:"emergency_contact,omitempty" bson:"emergency_contact,omitempty" binding:"max=2,dive" encryption:"true"`
	DiscordID        string             `json:"discord_id,omitempty" bson:"discord_id,omitempty" binding:"max=30"`
	Introduction     string             `json:"introduction,omitempty" bson:"introduction,omitempty" binding:"max=1000" encryption:"true"`
	CurrentGroup     string             `json:"current_group,omitempty" bson:"current_group,omitempty"`
	TeamLeader       string             `json:"team_leader,omitempty" bson:"team_leader,omitempty" binding:"max=30"`
	ApplyMessage     string             `json:"apply_message,omitempty" bson:"apply_message,omitempty" binding:"max=200"`
	PermissionLevel  int                `json:"permission_level,omitempty" bson:"permission_level,omitempty"`
}

type GetStaff struct {
	UUID            string `json:"uuid" bson:"_id"`
	Email           string `json:"email" bson:"email"`
	OfficialEmail   string `json:"official_email" bson:"official_email"`
	HighSchoolStage string `json:"high_school_stage" bson:"high_school_stage"`
	DiscordID       string `json:"discord_id,omitempty" bson:"discord_id,omitempty"`
	CurrentGroup    string `json:"current_group" bson:"current_group"`
	PermissionLevel int    `json:"permission_level" bson:"permission_level"`
	TeamLeader      string `json:"team_leader,omitempty" bson:"team_leader,omitempty" binding:"max=30"`
	ApplyMessage    string `json:"apply_message,omitempty" bson:"apply_message,omitempty" binding:"max=30"`
}

type EmergencyContact struct {
	Name         string `json:"name" bson:"name" binding:"required,max=10" encryption:"true"`
	Relationship string `json:"relationship" bson:"relationship" binding:"required,max=10" encryption:"true"`
	Phone        string `json:"phone" bson:"phone" binding:"required,max=10" encryption:"true"`
}
