package com.example.controller;

public class RegisterUserRequest {

    private String email;
    private String password;
    private String nickname;

    public RegisterUserRequest(String email, String password, String nickname) {
        this.email = email;
        this.password = password;
        this.nickname = nickname;
    }

    public String getEmail() {
        return email;
    }

    public String getPassword() {
        return password;
    }

    public String getNickname() {
        return nickname;
    }
}