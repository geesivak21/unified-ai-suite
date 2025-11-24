def run():
    import streamlit as st
    import pandas as pd
    import glob
    import os
    from io import BytesIO
    from openai import AzureOpenAI
    from rapidfuzz import process, fuzz
    from procurement_ai.config import (
        azure_api_key,
        azure_api_version,
        azure_endpoint,
        azure_deployment
    )
    from sqlalchemy import create_engine
    from langchain_community.utilities import SQLDatabase
    from langchain_community.agent_toolkits import SQLDatabaseToolkit
    from langchain.agents import create_agent
    from langchain_openai import AzureChatOpenAI
    from streamlit_mic_recorder import mic_recorder
    from streamlit_mic_recorder import mic_recorder
    from procurement_ai.transcript import get_transcripts

    # ==============================
    # 🔧 Initialize Azure OpenAI Client
    # ==============================
    client = AzureOpenAI(
        api_version=azure_api_version,
        azure_endpoint=azure_endpoint,
        api_key=azure_api_key,
    )

    # ==============================
    # ⚙️ Streamlit Configuration
    # ==============================
    st.set_page_config(page_title="Procurement AI Dashboard", layout="wide")
    st.title("🏭 Procurement AI Dashboard")
    st.markdown("Analyze vendor pricing, detect naming inconsistencies, and get AI-powered insights across multiple plants.")

    # ==============================
    # 🧹 Clear State Utility
    # ==============================
    def clear_all_state():
        for key in list(st.session_state.keys()):
            del st.session_state[key]

        # Reset the plant selector widget explicitly
        st.session_state["plant_selector"] = []

        st.toast("✅ Cleared selections and results.")
        st.rerun()

    # ==============================
    # 📁 Load Available Plant Files
    # ==============================
    DATA_DIR = "datasets"
    if not os.path.exists(DATA_DIR):
        st.error(f"❌ Folder '{DATA_DIR}' not found. Please ensure it exists.")
        st.stop()

    available_files = sorted(glob.glob(os.path.join(DATA_DIR, "Plant_*.xlsx")))
    plant_names = [os.path.splitext(os.path.basename(f))[0].replace("Plant_", "") for f in available_files]

    if not plant_names:
        st.warning("⚠️ No plant files found in the datasets folder (e.g., Plant_1300.xlsx).")
        st.stop()

    # ==============================
    # 🌱 Multi-select for Plants
    # ==============================
    selected_plants = st.multiselect("🏭 Select Plants for Analysis", plant_names, key="plant_selector")

    if st.button("🔄 Clear Selection"):
        clear_all_state()

    if not selected_plants:
        st.info("👆 Please select one or more plants to begin analysis.")
        st.stop()

    # ==============================
    # 📚 Load Data from Selected Plants
    # ==============================
    @st.cache_data(show_spinner=False)
    def load_selected_plants(plants):
        df_list = []
        for p in plants:
            file_path = os.path.join(DATA_DIR, f"Plant_{p}.xlsx")
            if os.path.exists(file_path):
                temp_df = pd.read_excel(file_path)
                temp_df["Plant"] = p  # tag plant if not already
                df_list.append(temp_df)
        return pd.concat(df_list, ignore_index=True) if df_list else pd.DataFrame()

    df = load_selected_plants(selected_plants)

    if df.empty:
        st.error("⚠️ No data found in the selected files.")
        st.stop()

    # --- Clean & Standardize ---
    df['Net Price'] = pd.to_numeric(df['Net Price'], errors='coerce')
    df['Quantity in SKU'] = pd.to_numeric(df.get('Quantity in SKU', 0), errors='coerce')
    df = df.dropna(subset=['Plant'])

    # ===================================================
    # 🧭 Tabs
    # ===================================================
    tab1, tab2, tab3, tab4 = st.tabs(["💰 Cheapest Vendor Finder", 
                                    "🧩 Short Text Similarity Check",
                                    "📦 Material Net Price Across Plants",
                                    "💬 Procurement Chatbot (SQL Agent)"])


    # ===================================================
    # 💰 TASK 1 - Cheapest Vendor Finder
    # ===================================================
    with tab1:
        st.subheader("💰 Cheapest Vendor Finder & AI Insights")
        st.markdown("Analyze the cheapest vendor for each material across selected plants.")

        if st.button("▶️ Run Cheapest Vendor Analysis", key="run_task1"):
            # --- Vendor Count per Material ---
            vendor_counts = (
                df.groupby(['Plant', 'Material'])['Supplier/Supplying Plant']
                .nunique()
                .reset_index(name='vendor_count')
            )
            df = pd.merge(df, vendor_counts, on=['Plant', 'Material'], how='left')

            # --- Smart Zero-Price Handling ---
            df_valid = df[(df['vendor_count'] == 1) | (df['Net Price'] > 0)].copy()

            # --- Cheapest Vendor Calculation ---
            min_idx = df_valid.groupby(['Plant', 'Material'])['Net Price'].idxmin()
            cheapest_df = df_valid.loc[min_idx, [
                'Plant', 'Material', 'Supplier/Supplying Plant', 'Short Text', 'Net Price', 'Currency'
            ]].reset_index(drop=True)

            # --- Summary Statistics ---
            summary_df = (
                df_valid.groupby(['Plant', 'Material'])
                .agg(
                    avg_price=('Net Price', 'mean'),
                    min_price=('Net Price', 'min'),
                    max_price=('Net Price', 'max'),
                    vendor_count=('Supplier/Supplying Plant', 'nunique')
                )
                .reset_index()
            )

            st.session_state["cheapest_df"] = cheapest_df
            st.session_state["summary_df"] = summary_df
            st.session_state["df_valid"] = df_valid
            st.success("✅ Cheapest Vendor Analysis Completed!")

        if "cheapest_df" in st.session_state:
            cheapest_df = st.session_state["cheapest_df"]
            summary_df = st.session_state["summary_df"]
            df_valid = st.session_state["df_valid"]

            for plant in sorted(df_valid['Plant'].unique()):
                st.markdown(f"## 🌿 Plant {plant}")
                filtered_cheapest = cheapest_df[cheapest_df['Plant'] == plant]
                filtered_summary = summary_df[summary_df['Plant'] == plant]

                st.markdown(f"### 💰 Cheapest Vendors per Material (Plant {plant})")
                st.dataframe(filtered_cheapest, width="stretch")

                # --- Material Summary (All Vendors) ---
                st.markdown(f"### 📗 Material Price Summary (All Vendors) — Plant {plant}")
                st.dataframe(filtered_summary, width="stretch")

                multi_vendor_materials = filtered_summary[filtered_summary['vendor_count'] > 1]['Material'].unique()
                if len(multi_vendor_materials) > 0:
                    st.markdown("💡 Expand below to view materials with multiple vendors.")
                    limit = st.slider(f"🔢 Limit materials for Plant {plant}", 5, 50, 10, key=f"exp_limit_{plant}")
                    for material in multi_vendor_materials[:limit]:
                        with st.expander(f"🔧 Material: {material} — Vendor Comparison ({plant})"):
                            mat_df = df_valid[(df_valid['Plant'] == plant) & (df_valid['Material'] == material)]
                            mat_df = mat_df[['Supplier/Supplying Plant', 'Short Text', 'Net Price', 'Currency']].sort_values('Net Price')
                            cheapest_price = mat_df['Net Price'].replace(0, float('inf')).min()
                            mat_df['Cheapest?'] = mat_df['Net Price'].apply(lambda x: "✅ Yes" if x == cheapest_price else "")
                            st.dataframe(mat_df, width="stretch")
                else:
                    st.info(f"No materials with multiple vendors found for Plant {plant}.")

            # --- AI Insights ---
            st.markdown("### 🤖 AI-Generated Insights")
            selected_plant_for_ai = st.selectbox("Select Plant for AI Summary", sorted(df_valid['Plant'].unique()))
            if st.button("Generate Insights", key="generate_ai"):
                plant_data = summary_df[summary_df["Plant"] == selected_plant_for_ai]
                insight_prompt = f"""
                You are an expert procurement analyst.

                Task:
                Summarize pricing trends for Plant {selected_plant_for_ai}.

                Focus on:
                - Vendors offering consistently lowest prices.
                - Materials showing high price variance.
                - Potential savings or anomalies.
                - Recommendations for negotiation or sourcing.

                Respond in concise business English, 3-5 bullet points maximum.

                Data Summary:
                {plant_data.head(20).to_string(index=False)}
                """

                with st.spinner("Generating insights with Azure OpenAI..."):
                    response = client.chat.completions.create(
                        messages=[
                            {"role": "system", "content": "You are an expert procurement analyst."},
                            {"role": "user", "content": insight_prompt}
                        ],
                        max_tokens=2048,
                        temperature=0.0,
                        model=azure_deployment
                    )
                    st.session_state["ai_insights"] = response.choices[0].message.content

            if "ai_insights" in st.session_state:
                st.success("AI Insights:")
                st.write(st.session_state["ai_insights"])

    # ===================================================
    # 🧩 TASK 2 - Short Text Similarity Check (with Vendor-Price Mapping)
    # ===================================================
    with tab2:
        st.subheader("🧩 Short Text Similarity Check (Detect Naming Typos per Plant with Vendor Prices)")

        def find_similar_blocked_full(df, text_col="Short Text", threshold=90):
            """
            Finds similar short texts per plant after removing duplicates and symmetric pairs.
            Adds both Material (Short Text) and Material (Similar To) columns.
            Also includes vendor → price mapping for each material.
            """
            df = df.copy()
            df[text_col] = df[text_col].astype(str).str.strip()

            # ✅ Remove duplicates by Plant + Short Text
            df = df.drop_duplicates(subset=["Plant", text_col])

            # ✅ Create vendor-price map per material
            vendor_price_map = (
                df.groupby(["Plant", "Material"])
                .apply(lambda g: {str(v): float(p) for v, p in zip(g["Supplier/Supplying Plant"], g["Net Price"])})
                .to_dict()
            )

            # Group by first 3 words for fuzzy efficiency
            df["Group"] = df[text_col].str.split().str[:3].apply(lambda x: " ".join(x))
            groups = list(df.groupby(["Plant", "Group"]))
            total_groups = len(groups)

            progress_text = st.empty()
            progress_bar = st.progress(0)
            results = []

            for i, ((plant, prefix), group) in enumerate(groups, start=1):
                texts = group[text_col].tolist()

                if len(texts) == 1:
                    material = group.loc[group[text_col] == texts[0], "Material"].iloc[0]
                    results.append({
                        "Plant": plant,
                        text_col: texts[0],
                        "Material (Short Text)": material,
                        "Vendor_Price_Map (Short Text)": vendor_price_map.get((plant, material), {}),
                        "Similar_To": None,
                        "Material (Similar To)": None,
                        "Vendor_Price_Map (Similar_To)": {},
                        "Similarity_Score": 0,
                        "Flag": "No Similar Found"
                    })
                else:
                    for text in texts:
                        material_text = group.loc[group[text_col] == text, "Material"].iloc[0]
                        similar = process.extract(text, texts, scorer=fuzz.token_sort_ratio, limit=3)
                        best_match = next(((cand, score) for cand, score, _ in similar if cand != text), (None, 0))

                        if best_match[0] is not None:
                            material_similar = (
                                group.loc[group[text_col] == best_match[0], "Material"].iloc[0]
                                if best_match[0] in group[text_col].values else None
                            )
                        else:
                            material_similar = None

                        flag = "Similar Found" if best_match[1] >= threshold else "No Similar Found"

                        if flag == "Similar Found":
                            results.append({
                                "Plant": plant,
                                text_col: text,
                                "Material (Short Text)": material_text,
                                "Vendor_Price_Map (Short Text)": vendor_price_map.get((plant, material_text), {}),
                                "Similar_To": best_match[0],
                                "Material (Similar To)": material_similar,
                                "Vendor_Price_Map (Similar_To)": vendor_price_map.get((plant, material_similar), {}),
                                "Similarity_Score": round(best_match[1], 2),
                                "Flag": flag
                            })

                progress_bar.progress(i / total_groups)
                progress_text.markdown(f"🔍 Processing group {i}/{total_groups} — Plant: `{plant}` | Prefix: `{prefix}`")

            progress_bar.empty()
            progress_text.markdown("✅ Similarity analysis complete.")

            result_df = pd.DataFrame(results)

            # ✅ Remove symmetric duplicates (A↔B)
            if not result_df.empty:
                result_df["pair_key"] = result_df.apply(
                    lambda x: "_".join(sorted([str(x["Short Text"]), str(x["Similar_To"])])), axis=1
                )
                result_df = result_df.drop_duplicates(subset=["Plant", "pair_key"])
                result_df = result_df.drop(columns=["pair_key"], errors="ignore")

            return result_df

        # --- Similarity Settings ---
        threshold = st.slider("Select similarity threshold (%)", 70, 100, 90, key="sim_threshold")

        if st.button("Run Similarity Check Across Plants", key="run_similarity"):
            with st.spinner("Analyzing Short Texts for potential typos and vendor prices..."):
                result_similarity = find_similar_blocked_full(df, "Short Text", threshold)
            st.session_state["result_similarity"] = result_similarity
            st.success("✅ Similarity check completed!")

        # --- Display Results ---
        if "result_similarity" in st.session_state:
            result_similarity = st.session_state["result_similarity"]
            show_flagged = st.checkbox("Show only flagged entries (Similar Found)", value=True)

            for plant in sorted(result_similarity["Plant"].unique()):
                st.markdown(f"## 🌿 Plant {plant}")
                plant_df = result_similarity[result_similarity["Plant"] == plant]
                result_view = plant_df[plant_df["Flag"] == "Similar Found"] if show_flagged else plant_df

                # Safe column order (avoid KeyErrors)
                display_cols = [
                    "Short Text",
                    "Material (Short Text)",
                    "Vendor_Price_Map (Short Text)",
                    "Similar_To",
                    "Material (Similar To)",
                    "Vendor_Price_Map (Similar_To)",
                    "Similarity_Score",
                    "Flag"
                ]

                st.dataframe(result_view.reindex(columns=display_cols), width="stretch", hide_index=True)

            # --- Download combined results ---
            output = BytesIO()
            result_similarity.to_excel(output, index=False, sheet_name="Similarity_Check")
            st.download_button(
                label="💾 Download Combined Results as Excel",
                data=output.getvalue(),
                file_name="MultiPlant_Similarity_Check.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            )

    # ===================================================
    # 📦 TASK 3 - Material Net Price Comparison + Anomaly Detection (SIMPLE & CORRECT)
    # ===================================================
    with tab3:
        st.subheader("📦 Material Price Comparison Across Plants (Anomaly Detection)")
        st.markdown("""
        Detect where **the same vendor quotes different prices**  
        for **the same material**, regardless of plant.

        ✔ Across same plant  
        ✔ Across multiple plants  
        ✔ Combining all plants together  
        """)

        if st.button("▶️ Run Material Comparison & Detect Anomalies", key="run_task3"):

            # Keep minimal required columns
            df_copy = df[[
                "Plant", "Material", "Supplier/Supplying Plant",
                "Short Text", "Net Price", "Currency"
            ]].copy()

            # Remove exact duplicate rows
            df_copy = df_copy.drop_duplicates()

            # Identify anomaly groups:
            # Same Material + Vendor having more than 1 unique Net Price
            group_cols = ["Material", "Supplier/Supplying Plant"]

            unique_price_count = (
                df_copy.groupby(group_cols)["Net Price"]
                .nunique()
                .reset_index(name="unique_prices")
            )

            # Anomaly = unique_prices > 1
            anomalies_key = unique_price_count[unique_price_count["unique_prices"] > 1]

            if anomalies_key.empty:
                st.session_state["anomalies"] = pd.DataFrame(columns=df_copy.columns)
                st.success("🎉 No anomalies detected — all vendor pricing is consistent!")
            else:
                # Merge to keep only anomaly rows
                anomalies = df_copy.merge(anomalies_key[group_cols], on=group_cols, how="inner")

                anomalies = anomalies.drop_duplicates()

                st.session_state["anomalies"] = anomalies

                # ⭐ TOTAL ANOMALY GROUP COUNT
                st.info(f"🔥 **{len(anomalies_key)} anomaly group(s) detected across selected plants.**")

        # ---------------- DISPLAY RESULTS -------------------
        if "anomalies" in st.session_state:
            anomalies = st.session_state["anomalies"]

            if anomalies.empty:
                st.info("🎉 No anomalies detected.")
            else:
                st.markdown("## 🔥 Detected Pricing Anomalies")

                # All unique anomaly pairs
                unique_pairs = anomalies[["Material", "Supplier/Supplying Plant"]].drop_duplicates()

                # Display count
                st.markdown(f"### Total Anomaly Groups: **{len(unique_pairs)}**")

                # Dropdown to show how many groups
                limit_options = ["5", "10", "20", "50", "ALL"]
                choice = st.selectbox("How many anomaly groups to display?", limit_options)

                limit = len(unique_pairs) if choice == "ALL" else int(choice)
                display_pairs = unique_pairs.head(limit)

                # ----------- function to show a group -------------
                def _show_group(material, vendor):
                    group_df = anomalies[
                        (anomalies["Material"] == material) &
                        (anomalies["Supplier/Supplying Plant"] == vendor)
                    ].sort_values(["Net Price", "Plant"])

                    group_df = group_df.drop_duplicates()

                    n_prices = group_df["Net Price"].nunique()

                    with st.expander(f"📦 Material: {material} | Vendor: {vendor} — {n_prices} price(s) found"):
                        st.dataframe(
                            group_df[["Plant", "Short Text", "Net Price", "Currency"]],
                            width="stretch",
                            hide_index=True
                        )

                # Render each anomaly group
                for _, row in display_pairs.iterrows():
                    _show_group(row["Material"], row["Supplier/Supplying Plant"])

                # -------- Download report --------
                output = BytesIO()
                anomalies.to_excel(output, index=False, sheet_name="Price_Anomalies")

                st.download_button(
                    label="💾 Download Full Anomaly Report",
                    data=output.getvalue(),
                    file_name="Material_Vendor_Anomalies.xlsx",
                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                )

    # ===================================================
    # 💬 TASK 4 - Procurement Chatbot (SQL Agent)
    # ===================================================

    @st.cache_resource
    def init_sql_agent():
        """Initialize SQL Database connection and LangChain SQL Agent."""
        engine = create_engine("sqlite:///procurement.db")
        db = SQLDatabase(engine)

        llm = AzureChatOpenAI(
            api_key=azure_api_key,
            api_version=azure_api_version,
            azure_endpoint=azure_endpoint,
            model=azure_deployment,
            temperature=0.0,
        )

        toolkit = SQLDatabaseToolkit(db=db, llm=llm)
        tools = toolkit.get_tools()

        system_prompt = f"""
        You are a procurement analysis assistant with SQL knowledge.
        You can query a relational database that contains columns like Plant, Material, Short Text,
        Supplier/Supplying Plant, Net Price, and Currency.

        When a user asks a question:
        - Convert it into a syntactically correct SQL SELECT query.
        - Always LIMIT to 10 results unless the user specifies otherwise.
        - Never modify data (no UPDATE, DELETE, INSERT, or DROP).
        - Retrieve relevant columns only (avoid SELECT *).
        - After fetching, summarize or explain results clearly like a procurement analyst.

        Database dialect: {db.dialect}.
        """

        agent = create_agent(llm, tools, system_prompt=system_prompt)
        return agent

    # --- Streamlit Chatbot UI ---
    with tab4:
        st.subheader("💬 Procurement Chatbot")
        st.markdown("""
        Ask procurement-related questions in plain English.
        The assistant will generate SQL queries, fetch data, and summarize insights for you.

        **Examples:**
        - “Which supplier gave the lowest price for Material 1001 across all plants?”
        - “List top 5 materials with the highest price variance.”
        - “Show average Net Price per Plant for Supplier ABC.”
        """)

        with st.spinner("Initializing SQL agent..."):
            agent = init_sql_agent()

        # --- Text Input Option ---
        st.markdown("### 💬 Type your question")
        user_query = st.text_input("Enter your procurement question:")

        if st.button("Ask", width="stretch") and user_query.strip():
            with st.spinner("Thinking..."):
                try:
                    response = agent.invoke({"messages": [{"role": "user", "content": user_query}]})
                    final_output = response["messages"][-1].content
                    st.success("✅ Response:")
                    st.markdown(final_output)
                except Exception as e:
                    st.error(f"❌ Error: {str(e)}")


        # --- OR Voice Input Option ---
        st.divider()
        st.markdown("### 🎙️ Or ask your question by voice:")

        # Mic recorder control
        audio_data = mic_recorder(
            start_prompt="🎤 Start recording",
            stop_prompt="🛑 Stop recording",
            just_once=False,
            use_container_width=True,
            
        )

        # Automatically process once recording stops
        if audio_data and audio_data.get("bytes"):
            st.audio(audio_data["bytes"], format="audio/wav")

            # Save audio locally
            file_name = "recorded_audio.wav"
            with open(file_name, "wb") as f:
                f.write(audio_data["bytes"])

            st.toast("✅ Audio recorded and saved!")

            # --- Step 1: Transcribe Audio ---
            with st.spinner("Transcribing your voice input..."):
                try:
                    transcribed_question = get_transcripts(file_name)
                    st.success(f"🗣️ Transcribed Question: **{transcribed_question}**")
                except Exception as e:
                    st.error(f"❌ Transcription error: {e}")
                    transcribed_question = None

            # --- Step 2: Generate Response ---
            if transcribed_question:
                with st.spinner("Generating response from SQL Agent..."):
                    try:
                        response = agent.invoke({"messages": [{"role": "user", "content": transcribed_question}]})
                        final_output = response["messages"][-1].content
                        st.success("✅ Response:")
                        st.markdown(final_output)
                    except Exception as e:
                        st.error(f"❌ Error generating response: {str(e)}")
            else:
                st.warning("⚠️ No audio detected. Please record your question first.")

