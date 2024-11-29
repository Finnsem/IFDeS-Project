document.addEventListener('DOMContentLoaded', function() {
    const fabButton = document.querySelector('.fab-container');
    const chatContainer = document.querySelector('.chat-container');
    const chatBody = document.getElementById('chat-body');
    const inputField = document.getElementById('chat-input-field');
    const searchForm = document.getElementById('searchForm');
    const loadingBarContainer = document.getElementById('loadingBarContainer');
    const loadingBar = document.getElementById('loadingBar');
    const loadingPercentage = document.getElementById('loadingPercentage');
    const resultItem = document.getElementById('resultItem');
    const aiAnalysis = document.getElementById('aiAnalysis');
    const suggestionsBox = document.getElementById('suggestions');
    
    let currentQuestionIndex = 0;
    let responses = [];
    let loadingInterval;

    // Question data
    const questions = [
        // (Questions as provided in the original code)
    ];

    // Show typing indicator
    function showTypingIndicator() {
        const typingIndicator = document.createElement('div');
        typingIndicator.classList.add('chat-message', 'bot-message');
        typingIndicator.innerHTML = `<strong>Scam Chat:</strong> <em>Typing...</em>`;
        chatBody.appendChild(typingIndicator);
        chatBody.scrollTop = chatBody.scrollHeight;
        return typingIndicator;
    }

    // Ask next question in chat
    function askNextQuestion() {
        if (currentQuestionIndex < questions.length) {
            const question = questions[currentQuestionIndex];
            const typingIndicator = showTypingIndicator();
            setTimeout(() => {
                typingIndicator.remove();
                addChatMessage("Scam Chat", question.question, 'bot-message');
                question.options.forEach(addChatOption);
            }, 1000);
        } else {
            processResponses();  // Show the summary with risk flags
        }
    }

    // Add message to chat
    function addChatMessage(sender, message, className = '') {
        const messageElement = document.createElement('div');
        messageElement.classList.add('chat-message', className);
        messageElement.innerHTML = `<strong>${sender}:</strong> ${message}`;
        chatBody.appendChild(messageElement);
        chatBody.scrollTop = chatBody.scrollHeight;
    }

    // Add chat option buttons
    function addChatOption(option) {
        const optionElement = document.createElement('button');
        optionElement.classList.add('chat-option');
        optionElement.innerText = option;
        optionElement.onclick = function() {
            handleUserResponse(option);
        };
        chatBody.appendChild(optionElement);
        chatBody.scrollTop = chatBody.scrollHeight;
    }

    // Handle user response in chat
    function handleUserResponse(response) {
        responses.push(response);
        addChatMessage("You", response, 'user-message');
        clearOptions();
        currentQuestionIndex++;
        askNextQuestion();
    }

    // Clear all options after a response
    function clearOptions() {
        document.querySelectorAll('.chat-option').forEach(option => option.remove());
    }

    // Process user responses and calculate risk level
    function processResponses() {
        // (Risk calculation logic as provided in the original code)
    }

    // Toggle chat display and initiate the first question
    if (fabButton) {
        fabButton.addEventListener('click', function() {
            if (!chatContainer.classList.contains('show')) {
                chatContainer.classList.toggle('show');
                askNextQuestion();
            }
        });
    }

    // Handle search form submission
    async function handleSearchSubmit(e) {
        e.preventDefault();
        const companyName = document.querySelector('.home-content__input').value.trim();
    
        if (companyName === "") {
            alert("Please enter a valid company name.");
            return;
        }
    
        // Reset and show loading bar
        loadingBarContainer.style.display = 'block';
        loadingBar.style.width = '0%';
        loadingPercentage.textContent = '0%';
        let progress = 0;
    
        loadingInterval = setInterval(() => {
            if (progress < 100) {
                progress += 10;
                loadingBar.style.width = `${progress}%`;
                loadingPercentage.textContent = `${progress}%`;
            }
        }, 200);
    
        try {
            const response = await fetch('/search', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ name: companyName }),
            });
    
            const data = await response.json();
            clearInterval(loadingInterval);
            loadingBarContainer.style.display = 'none';
    
            if (!data.success) {
                alert(data.message || "An error occurred.");
                return;
            }
    
            resultItem.innerHTML = `
                <span>${data.company_name}</span>
                <span>${data.remarks}</span>
                <span>${data.years}</span>
            `;
            aiAnalysis.innerHTML = data.ai_analysis;
    
        } catch (error) {
            clearInterval(loadingInterval);
            loadingBarContainer.style.display = 'none';
            console.error('Error:', error);
        }
    }
    

    // Handle search form submission with optimization
    if (searchForm) {
        searchForm.addEventListener('submit', handleSearchSubmit);
    }

    // Debounce input for search suggestions
    function debounce(func, delay) {
        let timeout;
        return function() {
            const context = this, args = arguments;
            clearTimeout(timeout);
            timeout = setTimeout(() => func.apply(context, args), delay);
        };
    }

    // Fetch suggestions for the search input
    async function searchSuggestions(query) {
        if (query.length === 0) {
            suggestionsBox.innerHTML = '';
            return;
        }

        try {
            const response = await fetch('/suggestions', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ name: query }),
            });

            const data = await response.json();
            suggestionsBox.innerHTML = '';

            if (data.suggestions && data.suggestions.length > 0) {
                data.suggestions.forEach(suggestion => {
                    const suggestionItem = document.createElement('div');
                    suggestionItem.classList.add('suggestion-item');
                    suggestionItem.textContent = suggestion;
                    suggestionItem.addEventListener('click', function() {
                        document.querySelector('.home-content__input').value = suggestion;
                        suggestionsBox.innerHTML = '';
                    });
                    suggestionsBox.appendChild(suggestionItem);
                });
            }
        } catch (error) {
            console.error('Error fetching suggestions:', error);
        }
    }

    // Attach suggestion fetching with debounce
    document.querySelector('.home-content__input').addEventListener('keyup', debounce(function() {
        searchSuggestions(this.value);
    }, 300));
});


document.addEventListener('DOMContentLoaded', function() {
    const profileDropdownButton = document.getElementById('profileDropdownButton');
    const profileDropdown = document.getElementById('profileDropdown');

    // Toggle the dropdown visibility when clicking on the profile picture
    profileDropdownButton.addEventListener('click', function(event) {
        event.stopPropagation(); // Prevent click from propagating to document
        profileDropdown.style.display = profileDropdown.style.display === 'block' ? 'none' : 'block';
    });

    // Close the dropdown if the user clicks outside of it
    document.addEventListener('click', function(event) {
        if (!profileDropdown.contains(event.target) && event.target !== profileDropdownButton) {
            profileDropdown.style.display = 'none';
        }
    });
});


// Show or hide the back-to-top button based on scroll position
window.onscroll = function() { toggleBackToTopButton() };

function toggleBackToTopButton() {
    const backToTopButton = document.querySelector('.back-to-top');
    if (document.body.scrollTop > 200 || document.documentElement.scrollTop > 200) {
        backToTopButton.style.display = "block";
    } else {
        backToTopButton.style.display = "none";
    }
}

// Scroll smoothly back to the top of the page
function scrollToTop() {
    window.scrollTo({ top: 0, behavior: 'smooth' });
}

function sendMessage() {
    const chatInput = document.getElementById("chatInput");
    const chatBody = document.getElementById("chatBody");
    const loadingIndicator = document.getElementById("loadingIndicator");
    const userMessage = chatInput.value.trim();

    if (userMessage) {
        // Append user's message to the chat
        const userMessageDiv = document.createElement("div");
        userMessageDiv.className = "message user-message";
        userMessageDiv.innerHTML = `<span>${userMessage}</span>`;
        chatBody.appendChild(userMessageDiv);

        // Clear input field and show loading indicator
        chatInput.value = "";
        loadingIndicator.style.display = "block";
        chatBody.scrollTop = chatBody.scrollHeight;

        // Simulate sending a request to the backend
        fetch("/chat/send", {
            method: "POST",
            headers: {
                "Content-Type": "application/json",
            },
            body: JSON.stringify({ message: userMessage }),
        })
        .then((response) => response.json())
        .then((data) => {
            // Append bot's response to the chat
            const botMessageDiv = document.createElement("div");
            botMessageDiv.className = "message bot-message";
            botMessageDiv.innerHTML = `<span>${data.response}</span>`;
            chatBody.appendChild(botMessageDiv);

            // Hide loading indicator
            loadingIndicator.style.display = "none";
            chatBody.scrollTop = chatBody.scrollHeight;
        })
        .catch((error) => {
            console.error("Error in fetch:", error);
            alert("Something went wrong. Please try again.");
        });
    }
}
