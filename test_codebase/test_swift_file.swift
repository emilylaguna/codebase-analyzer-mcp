import Foundation
import UIKit

// MARK: - Protocols
protocol DataProcessor {
    var isProcessing: Bool { get }
    func process(data: Data) -> Result<Data, Error>
    static func validate(data: Data) -> Bool
}

protocol NetworkDelegate: AnyObject {
    func didReceiveData(_ data: Data)
    func didFailWithError(_ error: Error)
}

// MARK: - Enums
enum NetworkError: Error, CaseIterable {
    case noConnection
    case timeout
    case invalidResponse
    case serverError(Int)
    
    var description: String {
        switch self {
        case .noConnection:
            return "No internet connection"
        case .timeout:
            return "Request timed out"
        case .invalidResponse:
            return "Invalid response format"
        case .serverError(let code):
            return "Server error with code: \(code)"
        }
    }
}

enum UserRole: String, Codable {
    case admin = "admin"
    case user = "user"
    case guest = "guest"
}

// MARK: - Structs
struct User: Codable, Identifiable {
    let id: UUID
    var name: String
    var email: String
    var role: UserRole
    var createdAt: Date
    
    init(id: UUID = UUID(), name: String, email: String, role: UserRole = .user) {
        self.id = id
        self.name = name
        self.email = email
        self.role = role
        self.createdAt = Date()
    }
    
    var displayName: String {
        return "\(name) (\(role.rawValue))"
    }
}

struct NetworkResponse<T: Codable> {
    let data: T
    let statusCode: Int
    let headers: [String: String]
    
    init(data: T, statusCode: Int, headers: [String: String] = [:]) {
        self.data = data
        self.statusCode = statusCode
        self.headers = headers
    }
}

// MARK: - Classes
class NetworkManager: NSObject {
    static let shared = NetworkManager()
    
    weak var delegate: NetworkDelegate?
    private var session: URLSession
    private var isConnected: Bool = false
    
    override init() {
        self.session = URLSession.shared
        super.init()
        setupSession()
    }
    
    deinit {
        session.invalidateAndCancel()
    }
    
    private func setupSession() {
        let config = URLSessionConfiguration.default
        config.timeoutIntervalForRequest = 30.0
        config.timeoutIntervalForResource = 60.0
        session = URLSession(configuration: config)
    }
    
    func connect() async throws -> Bool {
        // Simulate network connection
        try await Task.sleep(nanoseconds: 1_000_000_000)
        isConnected = true
        return true
    }
    
    func disconnect() {
        isConnected = false
    }
    
    func fetchData<T: Codable>(from url: URL) async throws -> NetworkResponse<T> {
        guard isConnected else {
            throw NetworkError.noConnection
        }
        
        let (data, response) = try await session.data(from: url)
        
        guard let httpResponse = response as? HTTPURLResponse else {
            throw NetworkError.invalidResponse
        }
        
        guard httpResponse.statusCode == 200 else {
            throw NetworkError.serverError(httpResponse.statusCode)
        }
        
        let decodedData = try JSONDecoder().decode(T.self, from: data)
        return NetworkResponse(data: decodedData, statusCode: httpResponse.statusCode)
    }
}

class UserManager: DataProcessor {
    static let shared = UserManager()
    
    var isProcessing: Bool = false
    private var users: [User] = []
    private let networkManager = NetworkManager.shared
    
    private init() {
        setupNetworkDelegate()
    }
    
    private func setupNetworkDelegate() {
        networkManager.delegate = self
    }
    
    func process(data: Data) -> Result<Data, Error> {
        isProcessing = true
        defer { isProcessing = false }
        
        do {
            let users = try JSONDecoder().decode([User].self, from: data)
            self.users = users
            let processedData = try JSONEncoder().encode(users)
            return .success(processedData)
        } catch {
            return .failure(error)
        }
    }
    
    static func validate(data: Data) -> Bool {
        do {
            _ = try JSONDecoder().decode([User].self, from: data)
            return true
        } catch {
            return false
        }
    }
    
    func addUser(_ user: User) {
        users.append(user)
    }
    
    func removeUser(withId id: UUID) {
        users.removeAll { $0.id == id }
    }
    
    func getUser(withId id: UUID) -> User? {
        return users.first { $0.id == id }
    }
    
    func getAllUsers() -> [User] {
        return users
    }
}

// MARK: - Extensions
extension UserManager: NetworkDelegate {
    func didReceiveData(_ data: Data) {
        let _ = process(data: data)
    }
    
    func didFailWithError(_ error: Error) {
        print("Network error: \(error.localizedDescription)")
    }
}

extension String {
    var isValidEmail: Bool {
        let emailRegex = "[A-Z0-9a-z._%+-]+@[A-Za-z0-9.-]+\\.[A-Za-z]{2,64}"
        let emailPredicate = NSPredicate(format: "SELF MATCHES %@", emailRegex)
        return emailPredicate.evaluate(with: self)
    }
    
    func truncated(to length: Int) -> String {
        if self.count <= length {
            return self
        }
        return String(self.prefix(length)) + "..."
    }
}

extension Array where Element == User {
    func filterByRole(_ role: UserRole) -> [User] {
        return self.filter { $0.role == role }
    }
    
    func sortByName() -> [User] {
        return self.sorted { $0.name < $1.name }
    }
}

// MARK: - Type Aliases
typealias UserCompletion = (Result<User, Error>) -> Void
typealias UsersCompletion = (Result<[User], Error>) -> Void
typealias NetworkCompletion<T> = (Result<NetworkResponse<T>, Error>) -> Void

// MARK: - Global Functions
func createTestUser(name: String, email: String) -> User {
    return User(name: name, email: email)
}

func validateUser(_ user: User) -> Bool {
    return !user.name.isEmpty && user.email.isValidEmail
}

// MARK: - Computed Properties and Subscripts
class DataStore {
    private var storage: [String: Any] = [:]
    
    subscript(key: String) -> Any? {
        get {
            return storage[key]
        }
        set {
            storage[key] = newValue
        }
    }
    
    var count: Int {
        return storage.count
    }
    
    var isEmpty: Bool {
        return storage.isEmpty
    }
}

// MARK: - Generics
class Cache<T: Codable> {
    private var items: [String: T] = [:]
    
    func set(_ item: T, forKey key: String) {
        items[key] = item
    }
    
    func get(forKey key: String) -> T? {
        return items[key]
    }
    
    func remove(forKey key: String) {
        items.removeValue(forKey: key)
    }
    
    func clear() {
        items.removeAll()
    }
}

// MARK: - Async/Await Example
actor AsyncDataProcessor {
    private var processedItems: [String] = []
    
    func processItem(_ item: String) async {
        // Simulate async processing
        try? await Task.sleep(nanoseconds: 1_000_000_000)
        processedItems.append(item)
    }
    
    func getProcessedItems() -> [String] {
        return processedItems
    }
}

// MARK: - Property Wrappers
@propertyWrapper
struct ValidatedEmail {
    private var value: String
    
    var wrappedValue: String {
        get { value }
        set {
            guard newValue.isValidEmail else {
                fatalError("Invalid email format")
            }
            value = newValue
        }
    }
    
    init(wrappedValue: String) {
        self.value = wrappedValue
    }
}

struct ValidatedUser {
    let name: String
    @ValidatedEmail var email: String
    
    init(name: String, email: String) {
        self.name = name
        self.email = email
    }
}

// MARK: - Main Usage Example
@main
struct SwiftTestApp {
    static func main() async {
        let userManager = UserManager.shared
        let networkManager = NetworkManager.shared
        
        // Create test users
        let user1 = createTestUser(name: "John Doe", email: "john@example.com")
        let user2 = createTestUser(name: "Jane Smith", email: "jane@example.com")
        
        // Add users to manager
        userManager.addUser(user1)
        userManager.addUser(user2)
        
        // Test network connection
        do {
            let isConnected = try await networkManager.connect()
            print("Network connected: \(isConnected)")
        } catch {
            print("Network connection failed: \(error)")
        }
        
        // Test data processing
        let users = userManager.getAllUsers()
        let userData = try? JSONEncoder().encode(users)
        
        if let data = userData {
            let result = userManager.process(data: data)
            switch result {
            case .success(let processedData):
                print("Data processed successfully: \(processedData.count) bytes")
            case .failure(let error):
                print("Data processing failed: \(error)")
            }
        }
        
        // Test async processing
        let asyncProcessor = AsyncDataProcessor()
        await asyncProcessor.processItem("item1")
        await asyncProcessor.processItem("item2")
        let processedItems = await asyncProcessor.getProcessedItems()
        print("Processed items: \(processedItems)")
        
        // Test cache
        let userCache = Cache<User>()
        userCache.set(user1, forKey: "user1")
        if let cachedUser = userCache.get(forKey: "user1") {
            print("Cached user: \(cachedUser.displayName)")
        }
        
        // Test validated user
        let validatedUser = ValidatedUser(name: "Test User", email: "test@example.com")
        print("Validated user: \(validatedUser.name) - \(validatedUser.email)")
        
        // Test data store
        let dataStore = DataStore()
        dataStore["test"] = "value"
        print("Data store count: \(dataStore.count)")
        
        // Test string extensions
        let testEmail = "test@example.com"
        print("Email valid: \(testEmail.isValidEmail)")
        print("Truncated string: \("This is a very long string".truncated(to: 10))")
        
        // Test array extensions
        let allUsers = userManager.getAllUsers()
        let adminUsers = allUsers.filterByRole(.admin)
        let sortedUsers = allUsers.sortByName()
        print("Total users: \(allUsers.count), Admin users: \(adminUsers.count)")
        
        // Test error handling
        for error in NetworkError.allCases {
            print("Error: \(error.description)")
        }
    }
} 