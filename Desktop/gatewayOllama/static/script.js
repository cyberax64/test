// Fonctions utilitaires
function copyToClipboard(text) {
    navigator.clipboard.writeText(text).then(() => {
        showNotification('Clé API copiée dans le presse-papier !', 'success');
    }).catch(() => {
        showNotification('Erreur lors de la copie', 'error');
    });
}

function showNotification(message, type = 'info') {
    const notification = document.createElement('div');
    notification.className = `notification notification-${type}`;
    notification.textContent = message;
    notification.style.cssText = `
        position: fixed;
        top: 20px;
        right: 20px;
        padding: 16px 24px;
        background: ${type === 'success' ? '#10b981' : type === 'error' ? '#ef4444' : '#667eea'};
        color: white;
        border-radius: 10px;
        box-shadow: 0 10px 30px rgba(0, 0, 0, 0.2);
        z-index: 10000;
        animation: slideInRight 0.3s ease;
    `;
    
    document.body.appendChild(notification);
    
    setTimeout(() => {
        notification.style.animation = 'slideOutRight 0.3s ease';
        setTimeout(() => notification.remove(), 300);
    }, 3000);
}

// Modal de création d'utilisateur
function showCreateUserModal() {
    const modal = document.getElementById('createUserModal');
    modal.classList.add('active');
}

function closeCreateUserModal() {
    const modal = document.getElementById('createUserModal');
    modal.classList.remove('active');
    document.getElementById('createUserForm').reset();
}

async function createUser(event) {
    event.preventDefault();
    
    const username = document.getElementById('new-username').value;
    const quota = document.getElementById('new-quota').value;
    
    try {
        const response = await fetch('/api/users', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                username: username,
                token_quota: parseInt(quota)
            })
        });
        
        const data = await response.json();
        
        if (response.ok) {
            showNotification(`Utilisateur ${username} créé avec succès !`, 'success');
            closeCreateUserModal();
            setTimeout(() => location.reload(), 1000);
        } else {
            showNotification(data.error || 'Erreur lors de la création', 'error');
        }
    } catch (error) {
        showNotification('Erreur de communication avec le serveur', 'error');
    }
}

// Édition du quota
async function editQuota(userId, currentQuota) {
    const newQuota = prompt(`Nouveau quota de tokens pour l'utilisateur:`, currentQuota);
    
    if (newQuota === null) return;
    
    const quotaInt = parseInt(newQuota);
    if (isNaN(quotaInt) || quotaInt < 0) {
        showNotification('Quota invalide', 'error');
        return;
    }
    
    try {
        const response = await fetch(`/api/users/${userId}/quota`, {
            method: 'PUT',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ quota: quotaInt })
        });
        
        if (response.ok) {
            showNotification('Quota mis à jour avec succès !', 'success');
            setTimeout(() => location.reload(), 1000);
        } else {
            showNotification('Erreur lors de la mise à jour', 'error');
        }
    } catch (error) {
        showNotification('Erreur de communication avec le serveur', 'error');
    }
}

// Activation/désactivation d'utilisateur
async function toggleUser(userId) {
    if (!confirm('Voulez-vous changer le statut de cet utilisateur ?')) {
        return;
    }
    
    try {
        const response = await fetch(`/api/users/${userId}/toggle`, {
            method: 'POST'
        });
        
        if (response.ok) {
            showNotification('Statut mis à jour avec succès !', 'success');
            setTimeout(() => location.reload(), 1000);
        } else {
            showNotification('Erreur lors de la mise à jour', 'error');
        }
    } catch (error) {
        showNotification('Erreur de communication avec le serveur', 'error');
    }
}

// Réinitialisation des tokens
async function resetTokens(userId) {
    if (!confirm('Voulez-vous réinitialiser le compteur de tokens de cet utilisateur ?')) {
        return;
    }
    
    try {
        const response = await fetch(`/api/users/${userId}/reset`, {
            method: 'POST'
        });
        
        if (response.ok) {
            showNotification('Tokens réinitialisés avec succès !', 'success');
            setTimeout(() => location.reload(), 1000);
        } else {
            showNotification('Erreur lors de la réinitialisation', 'error');
        }
    } catch (error) {
        showNotification('Erreur de communication avec le serveur', 'error');
    }
}

// Suppression d'utilisateur
async function deleteUser(userId, username) {
    if (!confirm(`Êtes-vous sûr de vouloir supprimer l'utilisateur "${username}" ?\n\nCette action est irréversible et supprimera également tout l'historique.`)) {
        return;
    }
    
    try {
        const response = await fetch(`/api/users/${userId}`, {
            method: 'DELETE'
        });
        
        if (response.ok) {
            showNotification('Utilisateur supprimé avec succès !', 'success');
            setTimeout(() => location.reload(), 1000);
        } else {
            showNotification('Erreur lors de la suppression', 'error');
        }
    } catch (error) {
        showNotification('Erreur de communication avec le serveur', 'error');
    }
}

// Fermeture du modal au clic en dehors
window.onclick = function(event) {
    const modal = document.getElementById('createUserModal');
    if (event.target === modal) {
        closeCreateUserModal();
    }
}

// Animations CSS personnalisées
const style = document.createElement('style');
style.textContent = `
    @keyframes slideInRight {
        from {
            transform: translateX(100%);
            opacity: 0;
        }
        to {
            transform: translateX(0);
            opacity: 1;
        }
    }
    
    @keyframes slideOutRight {
        from {
            transform: translateX(0);
            opacity: 1;
        }
        to {
            transform: translateX(100%);
            opacity: 0;
        }
    }
`;
document.head.appendChild(style);
