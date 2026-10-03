const SERVER_URL = "http://127.0.0.1:8765";


async function sendActiveTab(tabId) {

    try {

        // Get the active Chrome tab
        const tab = await chrome.tabs.get(tabId);

        const title = tab.title || "";
        const url = tab.url || "";


        console.log("==============================");
        console.log("ACTIVE TAB");
        console.log("Title:", title);
        console.log("URL:", url);
        console.log("==============================");


        // Send the information to Python
        const response = await fetch(
            SERVER_URL,
            {
                method: "POST",

                headers: {
                    "Content-Type": "application/json"
                },

                body: JSON.stringify({
                    title: title,
                    url: url
                })
            }
        );


        const result = await response.text();

        console.log(
            "Python response:",
            result
        );


    } catch (error) {

        console.error(
            "Could not contact Python:",
            error
        );

    }
}


// Detect when the user switches tabs
chrome.tabs.onActivated.addListener(
    (activeInfo) => {

        sendActiveTab(
            activeInfo.tabId
        );

    }
);


// Detect when a page finishes loading
chrome.tabs.onUpdated.addListener(
    (tabId, changeInfo) => {

        if (
            changeInfo.status === "complete"
        ) {

            sendActiveTab(tabId);

        }

    }
);  