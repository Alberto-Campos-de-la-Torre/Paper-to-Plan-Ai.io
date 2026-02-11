import React, { useState } from 'react';
import { X, Plus } from 'lucide-react';
import { createPatient, updatePatient, Patient } from '../api/client';

interface PatientFormModalProps {
    patient?: Patient;
    onClose: () => void;
    onCreated: () => void;
}

const PatientFormModal: React.FC<PatientFormModalProps> = ({ patient, onClose, onCreated }) => {
    const isEdit = !!patient;
    const [name, setName] = useState(patient?.name || '');
    const [dateOfBirth, setDateOfBirth] = useState(patient?.date_of_birth || '');
    const [gender, setGender] = useState(patient?.gender || '');
    const [bloodType, setBloodType] = useState(patient?.blood_type || '');
    const [contactPhone, setContactPhone] = useState(patient?.contact_phone || '');
    const [contactEmail, setContactEmail] = useState(patient?.contact_email || '');
    const [emergencyContact, setEmergencyContact] = useState(patient?.emergency_contact || '');
    const [notes, setNotes] = useState(patient?.notes || '');
    const [allergies, setAllergies] = useState<string[]>(patient?.allergies || []);
    const [conditions, setConditions] = useState<string[]>(patient?.conditions || []);
    const [newAllergy, setNewAllergy] = useState('');
    const [newCondition, setNewCondition] = useState('');
    const [submitting, setSubmitting] = useState(false);

    const addAllergy = () => {
        if (newAllergy.trim() && !allergies.includes(newAllergy.trim())) {
            setAllergies([...allergies, newAllergy.trim()]);
            setNewAllergy('');
        }
    };

    const addCondition = () => {
        if (newCondition.trim() && !conditions.includes(newCondition.trim())) {
            setConditions([...conditions, newCondition.trim()]);
            setNewCondition('');
        }
    };

    const handleSubmit = async (e: React.FormEvent) => {
        e.preventDefault();
        if (!name.trim()) return;

        setSubmitting(true);
        try {
            const data = {
                name: name.trim(),
                date_of_birth: dateOfBirth || undefined,
                gender: gender || undefined,
                blood_type: bloodType || undefined,
                allergies,
                conditions,
                cie10_codes: patient?.cie10_codes || [],
                contact_phone: contactPhone || undefined,
                contact_email: contactEmail || undefined,
                emergency_contact: emergencyContact || undefined,
                notes: notes || undefined,
            };

            if (isEdit && patient) {
                await updatePatient(patient.id, data);
            } else {
                await createPatient(data as any);
            }
            onCreated();
        } catch (error) {
            console.error("Error saving patient:", error);
            alert('Error al guardar paciente');
        } finally {
            setSubmitting(false);
        }
    };

    return (
        <div className="modal-overlay" onClick={onClose}>
            <div className="modal-content p-6" style={{ maxWidth: '600px' }} onClick={e => e.stopPropagation()}>
                <div className="flex justify-between items-center mb-4">
                    <h3 className="text-lg font-semibold">{isEdit ? 'Editar Paciente' : 'Nuevo Paciente'}</h3>
                    <button onClick={onClose} style={{ color: 'var(--color-text-muted)' }}>
                        <X className="w-5 h-5" />
                    </button>
                </div>

                <form onSubmit={handleSubmit} className="space-y-4 max-h-[65vh] overflow-y-auto pr-1">
                    <div>
                        <label className="block text-sm font-medium mb-1" style={{ color: 'var(--color-text-secondary)' }}>Nombre *</label>
                        <input type="text" value={name} onChange={e => setName(e.target.value)} className="input" placeholder="Nombre completo" required />
                    </div>

                    <div className="grid grid-cols-3 gap-3">
                        <div>
                            <label className="block text-sm font-medium mb-1" style={{ color: 'var(--color-text-secondary)' }}>Nacimiento</label>
                            <input type="date" value={dateOfBirth} onChange={e => setDateOfBirth(e.target.value)} className="input" />
                        </div>
                        <div>
                            <label className="block text-sm font-medium mb-1" style={{ color: 'var(--color-text-secondary)' }}>Genero</label>
                            <select value={gender} onChange={e => setGender(e.target.value)} className="input">
                                <option value="">-</option>
                                <option value="Masculino">Masculino</option>
                                <option value="Femenino">Femenino</option>
                                <option value="Otro">Otro</option>
                            </select>
                        </div>
                        <div>
                            <label className="block text-sm font-medium mb-1" style={{ color: 'var(--color-text-secondary)' }}>Tipo de Sangre</label>
                            <select value={bloodType} onChange={e => setBloodType(e.target.value)} className="input">
                                <option value="">-</option>
                                {['A+','A-','B+','B-','AB+','AB-','O+','O-'].map(bt => (
                                    <option key={bt} value={bt}>{bt}</option>
                                ))}
                            </select>
                        </div>
                    </div>

                    {/* Allergies */}
                    <div>
                        <label className="block text-sm font-medium mb-1" style={{ color: 'var(--color-text-secondary)' }}>Alergias</label>
                        <div className="flex flex-wrap gap-1 mb-2">
                            {allergies.map((a, i) => (
                                <span key={i} className="tag tag-allergy cursor-pointer" onClick={() => setAllergies(allergies.filter((_, j) => j !== i))}>
                                    {a} x
                                </span>
                            ))}
                        </div>
                        <div className="flex gap-2">
                            <input type="text" value={newAllergy} onChange={e => setNewAllergy(e.target.value)}
                                   onKeyDown={e => e.key === 'Enter' && (e.preventDefault(), addAllergy())}
                                   className="input flex-1" placeholder="Agregar alergia" />
                            <button type="button" onClick={addAllergy} className="btn btn-sm btn-outline">
                                <Plus className="w-3 h-3" />
                            </button>
                        </div>
                    </div>

                    {/* Conditions */}
                    <div>
                        <label className="block text-sm font-medium mb-1" style={{ color: 'var(--color-text-secondary)' }}>Condiciones</label>
                        <div className="flex flex-wrap gap-1 mb-2">
                            {conditions.map((c, i) => (
                                <span key={i} className="tag tag-condition cursor-pointer" onClick={() => setConditions(conditions.filter((_, j) => j !== i))}>
                                    {c} x
                                </span>
                            ))}
                        </div>
                        <div className="flex gap-2">
                            <input type="text" value={newCondition} onChange={e => setNewCondition(e.target.value)}
                                   onKeyDown={e => e.key === 'Enter' && (e.preventDefault(), addCondition())}
                                   className="input flex-1" placeholder="Agregar condicion" />
                            <button type="button" onClick={addCondition} className="btn btn-sm btn-outline">
                                <Plus className="w-3 h-3" />
                            </button>
                        </div>
                    </div>

                    <div className="grid grid-cols-2 gap-3">
                        <div>
                            <label className="block text-sm font-medium mb-1" style={{ color: 'var(--color-text-secondary)' }}>Telefono</label>
                            <input type="text" value={contactPhone} onChange={e => setContactPhone(e.target.value)} className="input" placeholder="(000) 000-0000" />
                        </div>
                        <div>
                            <label className="block text-sm font-medium mb-1" style={{ color: 'var(--color-text-secondary)' }}>Email</label>
                            <input type="email" value={contactEmail} onChange={e => setContactEmail(e.target.value)} className="input" placeholder="email@ejemplo.com" />
                        </div>
                    </div>

                    <div>
                        <label className="block text-sm font-medium mb-1" style={{ color: 'var(--color-text-secondary)' }}>Contacto de Emergencia</label>
                        <input type="text" value={emergencyContact} onChange={e => setEmergencyContact(e.target.value)} className="input" placeholder="Nombre y telefono" />
                    </div>

                    <div>
                        <label className="block text-sm font-medium mb-1" style={{ color: 'var(--color-text-secondary)' }}>Notas</label>
                        <textarea value={notes} onChange={e => setNotes(e.target.value)} className="input min-h-[60px] resize-y" placeholder="Observaciones generales..." />
                    </div>

                    <div className="flex gap-2 justify-end pt-2">
                        <button type="button" onClick={onClose} className="btn btn-outline">Cancelar</button>
                        <button type="submit" disabled={submitting || !name.trim()} className="btn btn-primary">
                            {submitting ? 'Guardando...' : isEdit ? 'Actualizar' : 'Crear Paciente'}
                        </button>
                    </div>
                </form>
            </div>
        </div>
    );
};

export default PatientFormModal;
