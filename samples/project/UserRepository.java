package com.example.repository;

import com.example.domain.User;

public interface UserRepository {

    boolean existsByEmail(String email);

    User save(User user);

    User findByEmail(String email);
}
