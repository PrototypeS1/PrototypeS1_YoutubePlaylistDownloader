def get_log_html(log_content):
    """Generates the HTML for the log area with updated appearance and minimal JavaScript for scrolling."""
    return f"""
    <html>
        <head>
            <style>
                .log-container {{
                    height: 300px; 
                    overflow-y: auto; 
                    border: 1px solid #ddd; 
                    padding: 10px; 
                    font-family: monospace;
                    background-color: #000; 
                    color: #0f0;
                    white-space: pre-wrap; /* Preserve whitespace and line breaks */
                    margin: 0;
                }}
            </style>
        </head>
        <body>
            <div class="log-container" id="log-container">
                <pre>{log_content}</pre>
            </div>
            <script>
                // Scroll to the bottom of the log container
                function scrollToBottom() {{
                    var container = document.getElementById('log-container');
                    container.scrollTop = container.scrollHeight;
                }}
                
                // Initial call to scroll to the bottom
                scrollToBottom();

                // Observe changes to the log content and scroll to bottom
                var observer = new MutationObserver(scrollToBottom);
                observer.observe(document.getElementById('log-container'), {{ childList: true, subtree: true }});
            </script>
        </body>
    </html>
    """
