import React from 'react';

interface MedicalTagsProps {
    items: string[];
    type: 'allergy' | 'condition' | 'cie10' | 'medication';
}

const MedicalTags: React.FC<MedicalTagsProps> = ({ items, type }) => {
    const getClass = () => {
        switch (type) {
            case 'allergy': return 'tag tag-allergy';
            case 'condition': return 'tag tag-condition';
            case 'cie10': return 'tag tag-cie10';
            case 'medication': return 'tag tag-medication';
        }
    };

    return (
        <>
            {items.map((item, i) => (
                <span key={i} className={getClass()}>{item}</span>
            ))}
        </>
    );
};

export default MedicalTags;
