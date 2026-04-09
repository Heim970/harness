@Service
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

        if (password.length() < 8) {
            throw new IllegalArgumentException("password too short");
        }

        if (userRepository.existsByEmail(email)) {
            throw new IllegalStateException("duplicate email");
        }

        String encoded = passwordEncoder.encode(password);

        User user = new User(email, encoded, nickname);

        return userRepository.save(user);
    }
}