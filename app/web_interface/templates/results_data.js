// Add hidden data element for JSON download
document.addEventListener('DOMContentLoaded', function() {
    // Create a hidden element to store the questions data
    const questionsDataElement = document.createElement('script');
    questionsDataElement.id = 'questions-data';
    questionsDataElement.type = 'application/json';
    questionsDataElement.textContent = JSON.stringify({
        metadata: {
            pdf_filename: "{{ metadata.pdf_filename }}",
            question_type: "{{ metadata.question_type }}",
            topic: "{{ metadata.topic }}",
            difficulty: "{{ metadata.difficulty }}",
            language: "{{ metadata.language }}",
            requested_count: {{ metadata.requested_count }},
            generated_count: {{ metadata.generated_count }},
            filtered_count: {{ metadata.filtered_count }},
            timestamp: "{{ metadata.timestamp }}"
        },
        questions: {{ questions|tojson }}
    });
    document.body.appendChild(questionsDataElement);
});
