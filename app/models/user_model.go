package models


type User struct {
	UUID              string             `json:"id,omitempty" bson:"_id" binding:"required,uuid"`
	IsRepresentative  bool               `json:"is_representative,omitempty" bson:"is_representative,omitempty" binding:"required,boolean"`
	TeamID            string             `json:"team_id" bson:"team_id" binding:"required"`
	Name              string             `json:"name,omitempty" bson:"name,omitempty" binding:"required"`
	Gender            string             `json:"gender,omitempty" bson:"gender,omitempty" binding:"required,oneof=male female other"`
	School            string             `json:"school,omitempty" bson:"school,omitempty" binding:"required"`
	Grade             string             `json:"grade,omitempty" bson:"grade,omitempty" binding:"required"`
	IdentityNumber    string             `json:"identity_number,omitempty" bson:"identity_number,omitempty" binding:"required,len=10"`
	StudentCardFront  string             `json:"student_card_front,omitempty" bson:"student_card_front,omitempty" binding:"required,base64"`
	StudentCardBack   string             `json:"student_card_back,omitempty" bson:"student_card_back,omitempty" binding:"required,base64"`
	UserNumber        int                `json:"user_number,omitempty" bson:"user_number,omitempty" binding:"required,number"`
	Birthday          string             `json:"birthday,omitempty" bson:"birthday,omitempty" binding:"required"`
	Email             string             `json:"email,omitempty" bson:"email,omitempty" binding:"required,email"`
	Phone             string             `json:"phone,omitempty" bson:"phone,omitempty" binding:"required,max=10,min=10"`
	EmergencyContacts []EmergencyContact `json:"emergency_contacts,omitempty" bson:"emergency_contacts,omitempty" binding:"required,max=2,dive"`
	TShirtSize        string             `json:"t_shirt_size,omitempty" bson:"t_shirt_size,omitempty" binding:"required,oneof=XS S M L XL"`
	Allergies         string             `json:"allergies,omitempty" bson:"allergies,omitempty" binding:"required"`
	SpecialDiseases   string             `json:"special_diseases,omitempty" bson:"special_diseases,omitempty" binding:"required"`
	Remarks           string             `json:"remarks,omitempty" bson:"remarks,omitempty" binding:"required"`
	VerificationCode  string             `json:"verification_code,omitempty" bson:"verification_code,omitempty" binding:"required,len=6"`
	CheckedIn         bool               `json:"checked_in,omitempty" bson:"checked_in,omitempty" binding:"required"`
	CreatedAt         int              `json:"created_at" bson:"created_at" binding:"required"`
	UpdatedAt         int              `json:"updated_at" bson:"updated_at" binding:"required"`
}
