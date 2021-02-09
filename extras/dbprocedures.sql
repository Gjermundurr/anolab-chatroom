CREATE PROCEDURE checkUser @Username nvarchar(30), @Email nvarchar(70)
AS
IF ((SELECT USER_NAME, EMAIL_ADDRESS FROM chatroom.users WHERE USER_NAME = @Username OR EMAIL_ADDRESS = @Email), "FOUND", "NOT_FOUND");
GO;
