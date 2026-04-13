package com.example.controller;

import com.example.domain.User;
import com.example.service.UserService;

public class UserController {

    private final UserService userService;

    public UserController(UserService userService) {
        this.userService = userService;
    }

    public User register(RegisterUserRequest request) {
        return userService.register(
                request.getEmail(),
                request.getPassword(),
                request.getNickname());
    }

    public User findUser(String email) {
        return userService.findByEmail(email);
    }
}