$(document).ready(function() {
    let page = 2;
    $('#load-more').click(function() {
        $.ajax({
            url: `/?page=${page}`,
            dataType: 'json',
            headers: {
                'X-Requested-With': 'XMLHttpRequest'
            },
            success: function(response) {
                if (response.questions.length > 0) {
                    response.questions.forEach(function(question) {
                        let questionHtml = `
                            <div class="d-flex mb-4 align-items-start">
                                <div class="d-flex align-items-center"></div>
                                <div class="card flex-grow-1">
                                    <div class="card-body">
                                        <h5 class="card-title">
                                            <a href="${question.url}" class="text-decoration-none text-primary">${question.title}</a>
                                        </h5>
                                        <p class="card-text">${question.content}</p>
                                        <span>${question.created_at}</span>
                                        <div class="mt-2">
                                            ${question.labels.map(label => `
                                            <span class="label" style="background-color: ${label.color}">${label.name}</span>`).join('')}
                                        </div>
                                    </div>
                                </div>
                            </div>
                        `;
                        $('#recent-questions').append(questionHtml);
                    });
                    page++;
                }
                if (!response.has_next) {
                    $('#load-more').hide();
                }
            }
        });
    });
});