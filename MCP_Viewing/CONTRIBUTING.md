# Contributing to MCP_Viewing

Thank you for your interest in contributing to MCP_Viewing! This document provides guidelines for development, testing, and contributing to the project.

## Development Setup

### Prerequisites

- Java 17 or higher
- Maven 3.6+
- Git
- Your favorite IDE (IntelliJ IDEA, Eclipse, VS Code with Java extensions)

### Clone and Build

```bash
git clone https://github.com/iau4u/MCP_Viewing.git
cd MCP_Viewing
mvn clean install
```

### Run the Application

```bash
mvn spring-boot:run
```

The application will start on `http://localhost:8080`.

### Run Tests

```bash
# Run all tests
mvn test

# Run specific test class
mvn test -Dtest=PartInfoControllerTest

# Run tests with coverage
mvn clean test jacoco:report
```

## Project Structure

```
src/main/java/com/mcpviewing/
├── config/          # Configuration classes (OpenAPI, etc.)
├── controller/      # REST controllers
├── dto/             # Data Transfer Objects
├── exception/       # Exception handlers
├── model/           # JPA entities
├── repository/      # JPA repositories
└── service/         # Business logic

src/test/java/com/mcpviewing/
├── controller/      # Controller unit tests
├── integration/     # Integration tests
└── service/         # Service unit tests
```

## Code Style

- Follow standard Java conventions
- Use Lombok annotations to reduce boilerplate code
- Write meaningful variable and method names
- Add JavaDoc comments for public APIs
- Keep methods small and focused

## Testing Guidelines

### Unit Tests

- Test individual components in isolation
- Use Mockito for mocking dependencies
- Focus on business logic
- Aim for high code coverage (>80%)

Example:
```java
@ExtendWith(MockitoExtension.class)
class PartInfoServiceTest {
    @Mock
    private PartInfoRepository repository;
    
    @InjectMocks
    private PartInfoService service;
    
    @Test
    void testGetPartInfoBySnr() {
        // given
        when(repository.findById("SNR-001")).thenReturn(Optional.of(partInfo));
        
        // when
        Optional<PartInfoResponse> result = service.getPartInfoBySnr("SNR-001");
        
        // then
        assertThat(result).isPresent();
    }
}
```

### Integration Tests

- Test complete workflows end-to-end
- Use embedded Derby database
- Test API contracts
- Verify database operations

Example:
```java
@SpringBootTest
@AutoConfigureMockMvc
class PartInfoIntegrationTest {
    @Autowired
    private MockMvc mockMvc;
    
    @Test
    void testCreateAndRetrievePartInfo() throws Exception {
        // Create
        mockMvc.perform(post("/api/partinfo")
                .contentType(MediaType.APPLICATION_JSON)
                .content(requestJson))
            .andExpect(status().isCreated());
        
        // Retrieve
        mockMvc.perform(get("/api/partinfo/SNR-001"))
            .andExpect(status().isOk());
    }
}
```

## Adding New Features

1. Create a feature branch:
   ```bash
   git checkout -b feature/your-feature-name
   ```

2. Implement your changes with tests

3. Ensure all tests pass:
   ```bash
   mvn clean verify
   ```

4. Commit your changes:
   ```bash
   git commit -m "Add feature: description"
   ```

5. Push and create a Pull Request

## Database Changes

When modifying the database schema:

1. Update the JPA entity in `model/PartInfo.java`
2. Hibernate will auto-update the schema (DDL-auto=update in development)
3. Add migration scripts for production if needed
4. Update tests to cover the new fields

## API Changes

When modifying the REST API:

1. Update the controller method
2. Update DTOs if needed
3. Update Swagger annotations
4. Update API documentation
5. Add/update tests
6. Update API_EXAMPLES.md

## Docker

### Build Docker Image

```bash
docker build -t mcp-viewing:latest .
```

### Run Docker Container

```bash
docker run -p 8080:8080 mcp-viewing:latest
```

### Test Docker Image

```bash
# Start container
docker run -d -p 8080:8080 --name mcp-test mcp-viewing:latest

# Wait for startup
sleep 10

# Test health endpoint
curl http://localhost:8080/actuator/health

# Stop container
docker stop mcp-test
docker rm mcp-test
```

## Continuous Integration

### Jenkins

The project uses Jenkins for CI/CD. The `Jenkinsfile` defines the pipeline:

1. Checkout
2. Build
3. Test
4. Package
5. Build Docker Image
6. Test Docker Image
7. Push to Registry (main branch only)
8. Deploy (main branch only)

### GitHub Actions

GitHub Actions workflows are defined in `.github/workflows/ci-cd.yml`:

1. Build and test on push/PR
2. Build Docker image
3. Run integration tests

## Logging

Use SLF4J with Lombok's `@Slf4j` annotation:

```java
@Slf4j
@Service
public class PartInfoService {
    public void someMethod() {
        log.debug("Debug message");
        log.info("Info message");
        log.warn("Warning message");
        log.error("Error message", exception);
    }
}
```

## Error Handling

- Use custom exceptions for business errors
- Let `GlobalExceptionHandler` handle exceptions globally
- Return appropriate HTTP status codes
- Provide meaningful error messages

## Security Considerations

- Always validate input data
- Use parameterized queries (JPA handles this)
- Don't log sensitive data
- Keep dependencies up-to-date

## Pull Request Guidelines

1. Ensure code compiles without errors
2. All tests must pass
3. Maintain or improve code coverage
4. Follow existing code style
5. Update documentation if needed
6. Provide a clear PR description
7. Link related issues

## Questions or Issues?

- Check existing issues on GitHub
- Create a new issue with a clear description
- Join discussions on Pull Requests

## License

By contributing, you agree that your contributions will be licensed under the Apache License 2.0.
