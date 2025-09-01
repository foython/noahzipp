(function () {
    const token = document.currentScript.getAttribute("data-token");
    const chatUrl = `http://localhost:5000/chat/${token}/`;
    let conversationHistory = [];
 
    // Create chatbot UI with Tailwind CSS and fixed height
    const chatContainer = document.createElement("div");
    chatContainer.innerHTML = `
<div class="fixed bottom-4 right-4 w-80 sm:w-96 h-[500px] bg-white rounded-lg shadow-xl flex flex-col z-50">
<div class="bg-gradient-to-r from-blue-600 to-blue-800 text-white p-4 rounded-t-lg flex items-center">
<img id="botProfilePic" class="w-10 h-10 rounded-full mr-3" src="" alt="Bot Avatar" style="display: none;">
<h3 class="text-lg font-semibold">Chat Assistant</h3>
</div>
<div id="chatOutput" class="flex-1 p-4 overflow-y-auto bg-gray-50"></div>
<div class="p-4 border-t">
<div class="flex space-x-2">
<input id="chatInput" type="text" placeholder="Type a message..." class="flex-1 p-2 border rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500">
<button onclick="sendMessage()" class="bg-blue-600 text-white px-4 py-2 rounded-lg hover:bg-blue-700 transition">Send</button>
</div>
</div>
</div>
    `;
    document.body.appendChild(chatContainer);
 
    // Load Tailwind CSS via CDN
    const tailwindLink = document.createElement("link");
    tailwindLink.rel = "stylesheet";
    tailwindLink.href = "https://cdn.jsdelivr.net/npm/tailwindcss@2.2.19/dist/tailwind.min.css";
    document.head.appendChild(tailwindLink);
 
    window.sendMessage = async function () {
        const input = document.getElementById("chatInput");
        const output = document.getElementById("chatOutput");
        const botProfilePic = document.getElementById("botProfilePic");
        const message = input.value.trim();
        if (!message) return;
 
        // Add user message to UI and history
        output.innerHTML += `
<div class="flex justify-end mb-2">
<div class="bg-blue-100 text-blue-900 p-2 rounded-lg max-w-[80%]">
                    ${message}
</div>
</div>
        `;
        conversationHistory.push({ role: "user", content: message });
        input.value = "";
        output.scrollTop = output.scrollHeight;
 
        try {
            const response = await fetch(chatUrl, {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({
                    message,
                    unique_id: token,
                    previous_conversation: conversationHistory
                })
            });
            const data = await response.json();
            if (response.ok) {
                // Add bot response to UI and history
                output.innerHTML += `
<div class="flex items-start mb-2">
<img src="${data.image}" class="w-8 h-8 rounded-full mr-2" alt="Bot Avatar">
<div class="bg-gray-200 text-gray-900 p-2 rounded-lg max-w-[80%]">
                            ${data.bot_response}
</div>
</div>
                `;
                conversationHistory.push({ role: "bot", content: data.bot_response });
 
                // Set bot profile picture if not already set
                if (botProfilePic.src !== data.image) {
                    botProfilePic.src = data.image;
                    botProfilePic.style.display = "block";
                }
            } else {
                output.innerHTML += `
<div class="text-red-500 text-sm mb-2">
                        Error: ${data.error}
</div>
                `;
            }
            output.scrollTop = output.scrollHeight;
        } catch (error) {
            output.innerHTML += `
<div class="text-red-500 text-sm mb-2">
                    Error: Failed to connect
</div>
            `;
            output.scrollTop = output.scrollHeight;
        }
    };
 
    document.getElementById("chatInput").addEventListener("keypress", (e) => {
        if (e.key === "Enter") sendMessage();
    });
})();


