import React from "react";

// Base Icon Wrapper for consistent sizing/color
const SvgIcon = ({ children, size = 24, color = "currentColor", ...props }) => (
    <svg
        xmlns="http://www.w3.org/2000/svg"
        width={size}
        height={size}
        viewBox="0 0 24 24"
        fill="none"
        stroke={color}
        strokeWidth="2"
        strokeLinecap="round"
        strokeLinejoin="round"
        {...props}
    >
        {children}
    </svg>
);

export const DashboardIcon = (props) => (
    <SvgIcon {...props}>
        <path d="M2 5a2 2 0 0 1 2-2h6v18H4a2 2 0 0 1-2-2V5Zm12-2h6a2 2 0 0 1 2 2v5h-8V3Zm0 11h8v5a2 2 0 0 1-2 2h-6v-7Z" />
    </SvgIcon>
);

export const StudentIcon = (props) => (
    // Student icon had a different viewBox (1024), so we override it
    <SvgIcon viewBox="0 0 1024 1024" fill="currentColor" stroke="none" {...props}>
        <path d="M990.848 696.304V438.16l16.096-8.496c10.464-5.44 17.055-16.225 17.183-28.032c.128-11.777-6.256-22.689-16.592-28.368l-481.44-257.6c-9.631-5.28-21.28-5.249-30.976.095l-478.8 257.92C6.126 379.36-.177 390.143-.113 401.84s6.496 22.4 16.817 27.97l210.384 111.983c-2.64 4.656-4.272 9.968-4.272 15.696v270.784a32.03 32.03 0 0 0 10.72 23.904c6.945 6.16 73.441 60.096 276.753 60.096c202.592 0 270.88-50.976 278-56.784c7.44-6.064 11.744-15.152 11.744-24.784V552.976c0-4.496-.944-8.768-2.608-12.64l129.424-68.369V696.48c-18.976 11.104-31.84 31.472-31.84 55.024c0 35.344 28.656 64 64 64s64-28.656 64-64c0-23.697-13.04-44.145-32.16-55.2zM736.031 812.368c-25.152 12.096-91.712 35.904-225.744 35.904c-134.88 0-199.936-25.344-223.472-37.536V573.6l207.808 110.624a31.896 31.896 0 0 0 15.184 3.84a31.675 31.675 0 0 0 14.816-3.664l211.408-111.664v239.632zM510.063 619.81l-411.6-218.561l412.32-220.976l413.6 220.336z"/>
    </SvgIcon>
);

export const TeacherIcon = (props) => (
    <SvgIcon strokeWidth="1.5" {...props}>
        <path d="M2 2h14c1.886 0 2.828 0 3.414.586S20 4.114 20 6v6c0 1.886 0 2.828-.586 3.414S17.886 16 16 16H9m1-9.5h6M2 17v-4c0-.943 0-1.414.293-1.707S3.057 11 4 11h2m-4 6h4m-4 0v5m4-5v-6m0 6v5m0-11h6"/>
        <path d="M6 6.5a2 2 0 1 1-4 0a2 2 0 0 1 4 0"/>
    </SvgIcon>
);

export const SchoolsIcon = (props) => (
    <SvgIcon viewBox="0 0 48 48" strokeWidth="4" {...props}>
        <path d="M4 33a2 2 0 0 1 2-2h6v-7l12-8l12 8v7h6a2 2 0 0 1 2 2v9a2 2 0 0 1-2 2H4V33Z"/>
        <path d="M24 6v10"/>
        <path d="M36 12V6s-1.5 3-6 0s-6 0-6 0v6s1.5-3 6 0s6 0 6 0Zm-8 32V31h-8v13m-2 0h12"/>
    </SvgIcon>
);

export const AllocationIcon = (props) => (
    <SvgIcon viewBox="0 0 48 48" strokeWidth="4" {...props}>
        <circle cx="8" cy="10" r="4" />
        <path d="M24 5l4 2v5l-4 2l-4-2V7z" />
        <rect x="34" y="6" width="9" height="9" rx="2" />

        <path d="M24 44V25" />
        <path d="M15 44v-5c0-4 9-4 9-4s9 0 9 4v5" />

        <path d="M24 25L11 14" />
        <path d="M24 25V15" />
        <path d="M24 25l13-11" />
    </SvgIcon>
);

export const SettingsIcon = (props) => (
    <SvgIcon {...props}>
        <circle cx="12" cy="12" r="3" />
        <path d="M19.4 15a1.65 1.65 0 0 0 .33 1.82l.06.06a2 2 0 0 1 0 2.83 2 2 0 0 1-2.83 0l-.06-.06a1.65 1.65 0 0 0-1.82-.33 1.65 1.65 0 0 0-1 1.51V21a2 2 0 0 1-2 2 2 2 0 0 1-2-2v-.09A1.65 1.65 0 0 0 9 19.4a1.65 1.65 0 0 0-1.82.33l-.06.06a2 2 0 0 1-2.83 0 2 2 0 0 1 0-2.83l.06-.06a1.65 1.65 0 0 0 .33-1.82 1.65 1.65 0 0 0-1.51-1H3a2 2 0 0 1-2-2 2 2 0 0 1 2-2h.09A1.65 1.65 0 0 0 4.6 9a1.65 1.65 0 0 0-.33-1.82l-.06-.06a2 2 0 0 1 0-2.83 2 2 0 0 1 2.83 0l.06.06a1.65 1.65 0 0 0 1.82.33H9a1.65 1.65 0 0 0 1-1.51V3a2 2 0 0 1 2-2 2 2 0 0 1 2 2v.09a1.65 1.65 0 0 0 1 1.51 1.65 1.65 0 0 0 1.82-.33l.06-.06a2 2 0 0 1 2.83 0 2 2 0 0 1 0 2.83l-.06.06a1.65 1.65 0 0 0-.33 1.82V9a1.65 1.65 0 0 0 1.51 1H21a2 2 0 0 1 2 2 2 2 0 0 1-2 2h-.09a1.65 1.65 0 0 0-1.51 1z" />
    </SvgIcon>
);

export const LogoutIcon = (props) => (
    <SvgIcon {...props}>
        <path d="M14 8V6a2 2 0 0 0-2-2H5a2 2 0 0 0-2 2v12a2 2 0 0 0 2 2h7a2 2 0 0 0 2-2v-2"/>
        <path d="M9 12h12l-3-3m0 6l3-3"/>
    </SvgIcon>
);