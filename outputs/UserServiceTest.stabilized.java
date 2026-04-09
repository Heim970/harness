package com.example.service;

import com.example.domain.User;
import com.example.repository.UserRepository;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.extension.ExtendWith;
import org.mockito.InjectMocks;
import org.mockito.Mock;
import org.mockito.junit.jupiter.MockitoExtension;
import org.springframework.security.crypto.password.PasswordEncoder;

import static org.junit.jupiter.api.Assertions.*;
import static org.mockito.ArgumentMatchers.any;
import static org.mockito.ArgumentMatchers.anyString;
import static org.mockito.Mockito.*;

@ExtendWith(MockitoExtension.class)
class UserServiceTest {

    @Mock
    private UserRepository userRepository;

    @Mock
    private PasswordEncoder passwordEncoder;

    @InjectMocks
    private UserService userService;

    @BeforeEach
    void setUp() {
        lenient().when(passwordEncoder.encode(anyString())).thenReturn("encodedPassword");
    }

    @Test
    void register_Success() {
        String email = "test@test.com";
        String password = "password123";
        String nickname = "tester";
        User user = new User(email, "encodedPassword", nickname);

        when(userRepository.existsByEmail(email)).thenReturn(false);
        when(userRepository.save(any(User.class))).thenReturn(user);

        User result = userService.register(email, password, nickname);

        assertNotNull(result);
        assertEquals(email, result.getEmail());
        verify(userRepository, times(1)).save(any(User.class));
    }

    @Test
    void register_ThrowsException_WhenEmailIsBlank() {
        assertThrows(IllegalArgumentException.class, () -> userService.register("", "password123", "nick"));
        assertThrows(IllegalArgumentException.class, () -> userService.register(null, "password123", "nick"));
        verifyNoInteractions(userRepository);
    }

    @Test
    void register_ThrowsException_WhenPasswordTooShort() {
        assertThrows(IllegalArgumentException.class, () -> userService.register("test@test.com", "1234567", "nick"));
        verifyNoInteractions(userRepository);
    }

    @Test
    void register_ThrowsException_WhenEmailDuplicate() {
        String email = "test@test.com";
        when(userRepository.existsByEmail(email)).thenReturn(true);

        assertThrows(IllegalStateException.class, () -> userService.register(email, "password123", "nick"));
        verify(userRepository, never()).save(any(User.class));
    }
}