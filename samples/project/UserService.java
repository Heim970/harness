package com.example.service;

import com.example.domain.User;
import com.example.repository.UserRepository;
import org.springframework.security.crypto.password.PasswordEncoder;

public class UserService {

    private final UserRepository userRepository;
    private final PasswordEncoder passwordEncoder;

    public UserService(UserRepository userRepository,
            PasswordEncoder passwordEncoder) {
        this.userRepository = userRepository;
        this.passwordEncoder = passwordEncoder;
    }

    public User register(String email, String password, String nickname) {
        if (email == null || email.isBlank()) {
            throw new IllegalArgumentException("email is required");
        }

        if (password == null) {
            throw new IllegalArgumentException("password is required");
        }

        if (password.length() < 8) {
            throw new IllegalArgumentException("password too short");
        }

        if (userRepository.existsByEmail(email)) {
            throw new IllegalStateException("duplicate email");
        }

        String encodedPassword = passwordEncoder.encode(password);
        User user = new User(email, encodedPassword, nickname);

        return userRepository.save(user);
    }

    public User findByEmail(String email) {
        if (email == null || email.isBlank()) {
            throw new IllegalArgumentException("email is required");
        }

        User user = userRepository.findByEmail(email);

        if (user == null) {
            throw new IllegalStateException("user not found");
        }

        return user;
    }

    public User changeNickname(String email, String newNickname) {
        if (email == null || email.isBlank()) {
            throw new IllegalArgumentException("email is required");
        }

        if (newNickname == null || newNickname.isBlank()) {
            throw new IllegalArgumentException("nickname is required");
        }

        User user = userRepository.findByEmail(email);

        if (user == null) {
            throw new IllegalStateException("user not found");
        }

        user.changeNickname(newNickname);

        return userRepository.save(user);
    }
}