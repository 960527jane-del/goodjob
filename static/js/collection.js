/**
 * F-06 寵物進化圖鑑 — 前端互動邏輯
 */

document.addEventListener('DOMContentLoaded', () => {
    initFilters();
    initAddExpButton();
    initEvolutionModal();
    animateOnLoad();
});

/* === 頁面載入動畫 === */
function animateOnLoad() {
    // 卡片交錯淡入
    const cards = document.querySelectorAll('.collection-card');
    cards.forEach((card, i) => {
        card.style.opacity = '0';
        card.style.transform = 'translateY(20px)';
        card.style.transition = 'opacity 0.4s ease, transform 0.4s ease';
        setTimeout(() => {
            card.style.opacity = '1';
            card.style.transform = 'translateY(0)';
        }, 80 + i * 60);
    });

    // 經驗值條動畫
    const expBar = document.getElementById('exp-bar-fill');
    if (expBar) {
        fetch('/api/pet/status')
            .then(r => r.json())
            .then(data => {
                if (data.exp_progress !== undefined) {
                    setTimeout(() => {
                        expBar.style.width = data.exp_progress + '%';
                    }, 300);
                    const expText = document.getElementById('exp-text');
                    if (expText) {
                        expText.textContent = `EXP ${data.exp_remaining} / ${data.exp_to_next_level}`;
                    }
                }
            })
            .catch(() => {});
    }
}

/* === 種族篩選 === */
function initFilters() {
    const filterBtns = document.querySelectorAll('.filter-btn');
    const cards = document.querySelectorAll('.collection-card');

    filterBtns.forEach(btn => {
        btn.addEventListener('click', () => {
            // 更新按鈕狀態
            filterBtns.forEach(b => b.classList.remove('active'));
            btn.classList.add('active');

            const species = btn.dataset.species;

            cards.forEach(card => {
                if (species === 'all' || card.dataset.species === species) {
                    card.classList.remove('hidden-by-filter');
                } else {
                    card.classList.add('hidden-by-filter');
                }
            });
        });
    });
}

/* === 開發用：加經驗值按鈕 === */
function initAddExpButton() {
    const btn = document.getElementById('add-exp-btn');
    if (!btn) return;

    btn.addEventListener('click', async () => {
        btn.disabled = true;
        btn.textContent = '⏳ 處理中...';

        try {
            const resp = await fetch('/api/pet/add-exp', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ exp: parseInt(btn.dataset.exp) })
            });
            const data = await resp.json();

            if (data.success) {
                // 更新等級顯示
                const levelBadge = document.querySelector('.level-badge');
                if (levelBadge) levelBadge.textContent = 'Lv.' + data.new_level;

                // 更新經驗值條
                updateExpBar();

                // 如果升級了
                if (data.leveled_up) {
                    btn.textContent = '🎉 升級了！';
                }

                // 如果進化了
                if (data.evolution && data.evolution.evolved) {
                    showEvolutionModal(data.evolution);
                } else {
                    setTimeout(() => {
                        btn.disabled = false;
                        btn.textContent = '⚡ +100 EXP';
                    }, 800);
                }
            }
        } catch (err) {
            console.error('加經驗值失敗:', err);
            btn.disabled = false;
            btn.textContent = '⚡ +100 EXP';
        }
    });
}

/* === 更新經驗值條 === */
async function updateExpBar() {
    try {
        const resp = await fetch('/api/pet/status');
        const data = await resp.json();

        const expBar = document.getElementById('exp-bar-fill');
        const expText = document.getElementById('exp-text');

        if (expBar) expBar.style.width = data.exp_progress + '%';
        if (expText) expText.textContent = `EXP ${data.exp_remaining} / ${data.exp_to_next_level}`;
    } catch (err) {
        console.error('更新經驗值條失敗:', err);
    }
}

/* === 進化彈窗 === */
function initEvolutionModal() {
    const confirmBtn = document.getElementById('evolution-confirm-btn');
    if (!confirmBtn) return;

    confirmBtn.addEventListener('click', () => {
        hideEvolutionModal();
        // 重新載入頁面以更新所有狀態
        window.location.reload();
    });

    // 點擊背景關閉
    const backdrop = document.getElementById('modal-backdrop');
    if (backdrop) {
        backdrop.addEventListener('click', () => {
            hideEvolutionModal();
            window.location.reload();
        });
    }
}

function showEvolutionModal(evolution) {
    const modal = document.getElementById('evolution-modal');
    if (!modal) return;

    // 填入進化資訊
    const oldEmoji = document.getElementById('evo-old-emoji');
    const newEmoji = document.getElementById('evo-new-emoji');
    const oldName = document.getElementById('evo-old-name');
    const newName = document.getElementById('evo-new-name');
    const desc = document.getElementById('evo-description');

    if (oldEmoji) oldEmoji.textContent = evolution.old_stage.emoji;
    if (newEmoji) newEmoji.textContent = evolution.new_stage.emoji;
    if (oldName) oldName.textContent = evolution.old_stage.name;
    if (newName) newName.textContent = evolution.new_stage.name;
    if (desc) desc.textContent = evolution.new_stage.description || '你的寵物進化成了全新的型態！';

    modal.style.display = 'flex';
}

function hideEvolutionModal() {
    const modal = document.getElementById('evolution-modal');
    if (modal) modal.style.display = 'none';
}
