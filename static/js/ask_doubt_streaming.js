async function sendUdaanQuestion(question, mode = "quick", history = []) {
    const response = await fetch(ASK_DOUBT_API_URL, {
        method: "POST",

        headers: {
            "Content-Type": "application/json",
            "X-CSRFToken": getCookie("csrftoken")
        },

        body: JSON.stringify({
            question: question,
            mode: mode,
            history: history,
            stream: true
        })
    });

    if (!response.ok) {
        const text = await response.text();
        throw new Error(
            text || "Udaan AI request failed."
        );
    }

    if (!response.body) {
        throw new Error(
            "Streaming is not supported by this browser."
        );
    }

    const reader = response.body.getReader();
    const decoder = new TextDecoder("utf-8");

    const assistantBubble = addAssistantMessage("");

    let fullAnswer = "";

    while (true) {
        const { value, done } = await reader.read();

        if (done) {
            break;
        }

        const chunk = decoder.decode(
            value,
            { stream: true }
        );

        fullAnswer += chunk;

        assistantBubble.textContent = fullAnswer;

        assistantBubble.scrollIntoView({
            behavior: "smooth",
            block: "end"
        });
    }

    return fullAnswer;
}


function addAssistantMessage(text) {
    const chatBox = document.getElementById(
        "chatMessages"
    );

    const bubble = document.createElement("div");

    bubble.className =
        "message assistant-message";

    bubble.textContent = text;

    chatBox.appendChild(bubble);

    return bubble;
}


function getCookie(name) {
    let cookieValue = null;

    if (
        document.cookie &&
        document.cookie !== ""
    ) {
        const cookies =
            document.cookie.split(";");

        for (
            let i = 0;
            i < cookies.length;
            i++
        ) {
            const cookie =
                cookies[i].trim();

            if (
                cookie.substring(
                    0,
                    name.length + 1
                ) ===
                (name + "=")
            ) {
                cookieValue =
                    decodeURIComponent(
                        cookie.substring(
                            name.length + 1
                        )
                    );

                break;
            }
        }
    }

    return cookieValue;
}